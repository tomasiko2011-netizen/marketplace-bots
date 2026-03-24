from __future__ import annotations

import argparse
import json
from pathlib import Path

from mp_bots.adapters.registry import get_adapter
from mp_bots.core.engine import evaluate_offers
from mp_bots.core.models import PriceRule
from mp_bots.db.sqlite import (
    get_excluded_products,
    get_settings,
    init_db,
    set_excluded_competitors,
    set_excluded_products,
    set_settings,
    upsert_offers,
    write_price_actions,
)


def _load_rules(path: str | None, args: argparse.Namespace) -> list[PriceRule]:
    rules: list[PriceRule] = []
    if path:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        for item in data.get("rules", []):
            rules.append(
                PriceRule(
                    sku=item.get("sku"),
                    category=item.get("category"),
                    min_price=item.get("min_price"),
                    max_price=item.get("max_price"),
                    undercut_by=item.get("undercut_by"),
                    priority=item.get("priority", 0),
                )
            )
    else:
        rules.append(
            PriceRule(
                min_price=args.min_price,
                max_price=args.max_price,
                undercut_by=args.undercut_by,
                priority=0,
            )
        )
    return rules


def _cmd_set_exclusions(args: argparse.Namespace) -> None:
    skus = [s.strip() for s in (args.skus or "").split(",") if s.strip()]
    competitors = [s.strip() for s in (args.competitors or "").split(",") if s.strip()]
    if skus:
        set_excluded_products(args.db, skus)
    if competitors:
        set_excluded_competitors(args.db, competitors)
    print(f"excluded_skus={len(skus)} excluded_competitors={len(competitors)}")


def cmd_init_db(args: argparse.Namespace) -> None:
    init_db(args.db)
    print(f"DB initialized at {args.db}")


def cmd_sync(args: argparse.Namespace) -> None:
    adapter_cls = get_adapter(args.marketplace)
    adapter = adapter_cls(mode=args.mode, input=args.input, api_base=args.api_base, token=args.token)

    offers = adapter.fetch_offers()
    excluded = get_excluded_products(args.db)
    if excluded:
        offers = [o for o in offers if o.sku not in excluded]
    upsert_offers(args.db, args.marketplace, offers)

    rules = _load_rules(args.rules, args)
    decisions = evaluate_offers(offers, rules)
    write_price_actions(args.db, decisions)

    if decisions:
        adapter.update_prices(decisions)

    print(f"offers={len(offers)} decisions={len(decisions)}")


def cmd_run(args: argparse.Namespace) -> None:
    import time

    if args.poll_interval is not None or args.turbo is not None:
        set_settings(args.db, poll_interval_seconds=args.poll_interval, turbo_mode=args.turbo)

    poll_interval_seconds, turbo_mode = get_settings(args.db)
    interval = 30 if turbo_mode else poll_interval_seconds

    for i in range(args.iterations):
        cmd_sync(args)
        if i < args.iterations - 1:
            time.sleep(interval)


def main() -> None:
    parser = argparse.ArgumentParser(prog="mp-bots")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init-db")
    p_init.add_argument("--db", required=True)
    p_init.set_defaults(func=cmd_init_db)

    p_sync = sub.add_parser("sync")
    p_sync.add_argument("--marketplace", required=True)
    p_sync.add_argument("--mode", choices=["mock", "live"], default="mock")
    p_sync.add_argument("--input", help="Path to mock offers JSON")
    p_sync.add_argument("--api-base", dest="api_base")
    p_sync.add_argument("--token")
    p_sync.add_argument("--db", required=True)
    p_sync.add_argument("--rules", help="Path to rules JSON")
    p_sync.add_argument("--min-price", type=float)
    p_sync.add_argument("--max-price", type=float)
    p_sync.add_argument("--undercut-by", type=float)
    p_sync.set_defaults(func=cmd_sync)

    p_run = sub.add_parser("run")
    p_run.add_argument("--marketplace", required=True)
    p_run.add_argument("--mode", choices=["mock", "live"], default="mock")
    p_run.add_argument("--input", help="Path to mock offers JSON")
    p_run.add_argument("--api-base", dest="api_base")
    p_run.add_argument("--token")
    p_run.add_argument("--db", required=True)
    p_run.add_argument("--rules", help="Path to rules JSON")
    p_run.add_argument("--min-price", type=float)
    p_run.add_argument("--max-price", type=float)
    p_run.add_argument("--undercut-by", type=float)
    p_run.add_argument("--poll-interval", type=int, help="Base interval in seconds (default 120)")
    p_run.add_argument("--turbo", action="store_true", help="Enable turbo mode (30 seconds)")
    p_run.add_argument("--iterations", type=int, default=1, help="Number of cycles to run")
    p_run.set_defaults(func=cmd_run)

    p_ex = sub.add_parser("set-exclusions")
    p_ex.add_argument("--db", required=True)
    p_ex.add_argument("--skus", help="Comma-separated SKUs to exclude")
    p_ex.add_argument("--competitors", help="Comma-separated competitor IDs to exclude")
    p_ex.set_defaults(func=lambda a: _cmd_set_exclusions(a))

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
