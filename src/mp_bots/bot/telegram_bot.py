from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

from mp_bots.adapters.registry import get_adapter
from mp_bots.core.engine import evaluate_offers
from mp_bots.core.models import PriceRule
from mp_bots.db.interface import DB, get_db

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Store helpers
# ---------------------------------------------------------------------------

def load_stores_from_config(config_path: str) -> List[Dict[str, Any]]:
    path = Path(config_path)
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("stores", [])


def find_store(stores: List[Dict[str, Any]], key: str) -> Dict[str, Any] | None:
    for s in stores:
        if s.get("key") == key:
            return s
    return None


def get_active_store(stores: List[Dict[str, Any]], db: DB, chat_id: int) -> Dict[str, Any] | None:
    key = db.get_session_store(chat_id)
    if key:
        return find_store(stores, key)
    if stores:
        return stores[0]
    return None


def build_adapter(store: Dict[str, Any]):
    adapter_cls = get_adapter(store["marketplace"])
    token_env = store.get("token_env")
    token = os.getenv(token_env) if token_env else None
    return adapter_cls(
        mode=store.get("mode", "live"),
        input=store.get("input"),
        api_base=store.get("api_base"),
        token=token,
    )


# ---------------------------------------------------------------------------
# Run cycle
# ---------------------------------------------------------------------------

def run_cycle(store: Dict[str, Any], db: DB) -> Dict[str, Any]:
    adapter = build_adapter(store)
    offers = adapter.fetch_offers()
    if not offers:
        return {"offers": 0, "decisions": 0, "blocked": False}

    plan_code, max_skus, paid_active, plan_started_at = db.get_plan(store["key"])
    if len(offers) > max_skus:
        return {
            "offers": len(offers),
            "decisions": 0,
            "blocked": True,
            "reason": f"Лимит {max_skus} SKU по тарифу {plan_code}",
        }

    excluded = db.get_excluded_products(store["key"])
    if excluded:
        offers = [o for o in offers if o.sku not in excluded]

    db.upsert_offers(store["key"], offers)

    min_price, max_price, undercut_by = db.get_rules(store["key"])
    rules = [PriceRule(min_price=min_price, max_price=max_price, undercut_by=undercut_by, priority=0)]
    decisions = evaluate_offers(offers, rules)
    db.write_price_actions(store["key"], decisions)

    if decisions:
        adapter.update_prices(decisions)

    return {"offers": len(offers), "decisions": len(decisions), "blocked": False}


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """Background scheduler that runs pricing cycles for all stores."""

    def __init__(self, stores: List[Dict[str, Any]], db: DB):
        self.stores = stores
        self.db = db
        self._running = False
        self._task: asyncio.Task | None = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._task = asyncio.ensure_future(self._loop())
        logger.info("Scheduler started")

    def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
        logger.info("Scheduler stopped")

    async def _loop(self):
        while self._running:
            for store in self.stores:
                try:
                    poll, turbo = self.db.get_settings(store["key"])
                    interval = 30 if turbo else poll
                    # Check if it's time to run (simple: always run, sleep per store)
                    stats = run_cycle(store, self.db)
                    if stats.get("blocked"):
                        logger.warning("Store %s blocked: %s", store["key"], stats.get("reason"))
                    elif stats["decisions"] > 0:
                        logger.info(
                            "Store %s: %d offers, %d decisions",
                            store["key"], stats["offers"], stats["decisions"],
                        )
                except Exception:
                    logger.exception("Scheduler error for store %s", store["key"])
            # Sleep for the shortest interval across all stores
            min_interval = self._min_interval()
            await asyncio.sleep(min_interval)

    def _min_interval(self) -> int:
        intervals = []
        for store in self.stores:
            try:
                poll, turbo = self.db.get_settings(store["key"])
                intervals.append(30 if turbo else poll)
            except Exception:
                intervals.append(120)
        return max(10, min(intervals)) if intervals else 120


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------

def nav_row() -> list[InlineKeyboardButton]:
    return [
        InlineKeyboardButton("⬅️ Назад", callback_data="nav:back"),
        InlineKeyboardButton("🏠 Домой", callback_data="nav:home"),
    ]


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📊 Статус", callback_data="menu:status")],
            [InlineKeyboardButton("▶️ Запустить 1 цикл", callback_data="menu:run_once")],
            [InlineKeyboardButton("🏪 Выбрать магазин", callback_data="menu:stores")],
            [InlineKeyboardButton("⚡ Турбо 30 сек", callback_data="menu:turbo")],
            [InlineKeyboardButton("⚙️ Настройки цен", callback_data="menu:rules")],
            [InlineKeyboardButton("🚫 Исключения товаров", callback_data="menu:exclude_sku")],
            [InlineKeyboardButton("🙅 Исключения конкурентов", callback_data="menu:exclude_competitor")],
            [InlineKeyboardButton("⏱ Базовый интервал", callback_data="menu:interval")],
            [InlineKeyboardButton("🧾 История изменений", callback_data="menu:history")],
            [InlineKeyboardButton("💳 Тарифы", callback_data="menu:tariffs")],
            [InlineKeyboardButton("✅ Выбрать тариф", callback_data="menu:choose_tariff")],
            [InlineKeyboardButton("🔄 Авто-запуск", callback_data="menu:scheduler")],
            nav_row(),
        ]
    )


# ---------------------------------------------------------------------------
# Bot handlers
# ---------------------------------------------------------------------------

def _get_db(context: ContextTypes.DEFAULT_TYPE) -> DB:
    return context.bot_data["db"]


def _get_stores(context: ContextTypes.DEFAULT_TYPE) -> List[Dict[str, Any]]:
    return context.bot_data["stores"]


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update, context):
        await update.message.reply_text("Доступ запрещен")
        return
    await update.message.reply_text(
        "skladprobot: главное меню",
        reply_markup=main_menu(),
    )


async def cmd_stores(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update, context):
        await update.message.reply_text("Доступ запрещен")
        return
    stores = _get_stores(context)
    if not stores:
        await update.message.reply_text("Список магазинов пуст")
        return
    buttons = [[InlineKeyboardButton(s.get("title", s["key"]), callback_data=f"store:{s['key']}")] for s in stores]
    await update.message.reply_text("Выберите магазин:", reply_markup=InlineKeyboardMarkup(buttons))


async def cmd_use(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update, context):
        await update.message.reply_text("Доступ запрещен")
        return
    db = _get_db(context)
    stores = _get_stores(context)
    if not context.args:
        await update.message.reply_text("Использование: /use <key>")
        return
    key = context.args[0]
    store = find_store(stores, key)
    if not store:
        await update.message.reply_text("Магазин не найден")
        return
    db.set_session_store(update.effective_chat.id, key)
    await update.message.reply_text(f"Выбран магазин: {key}", reply_markup=main_menu())


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update, context):
        await update.message.reply_text("Доступ запрещен")
        return
    db = _get_db(context)
    stores = _get_stores(context)
    store = get_active_store(stores, db, update.effective_chat.id)
    if not store:
        await update.message.reply_text("Нет доступных магазинов")
        return
    poll_interval, turbo = db.get_settings(store["key"])
    min_price, max_price, undercut_by = db.get_rules(store["key"])
    excluded = db.get_excluded_products(store["key"])
    excluded_comp = db.get_excluded_competitors(store["key"])
    plan_code, max_skus, paid_active, plan_started_at = db.get_plan(store["key"])
    trial_info = ""
    if not paid_active:
        used = db.get_run_count_checked(update.effective_chat.id, plan_started_at)
        trial_left = max(0, 5 - used)
        trial_info = f"Пробные запуски: осталось {trial_left}\n"
    scheduler: Scheduler | None = context.bot_data.get("scheduler")
    scheduler_status = "выключен"
    if scheduler and scheduler._running:
        scheduler_status = "работает"
    rule_text = (
        f"min={min_price} max={max_price} step={undercut_by}"
        if any(v is not None for v in (min_price, max_price, undercut_by))
        else "не заданы"
    )
    await update.message.reply_text(
        "Статус:\n"
        f"Магазин: {store['key']}\n"
        f"Интервал: {poll_interval} сек\n"
        f"Турбо: {'on' if turbo else 'off'}\n"
        f"Тариф: {plan_code} (лимит {max_skus} SKU) {'[оплачен]' if paid_active else '[trial]'}\n"
        + trial_info
        + f"Правила: {rule_text}\n"
        f"Исключено товаров: {len(excluded)}\n"
        f"Исключено конкурентов: {len(excluded_comp)}\n"
        f"Авто-запуск: {scheduler_status}"
    )


async def cmd_rules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update, context):
        await update.message.reply_text("Доступ запрещен")
        return
    db = _get_db(context)
    if len(context.args) != 3:
        await update.message.reply_text("Использование: /rules <min> <max> <step>")
        return
    min_price = float(context.args[0])
    max_price = float(context.args[1])
    step = float(context.args[2])
    store = get_active_store(_get_stores(context), db, update.effective_chat.id)
    if not store:
        await update.message.reply_text("Нет доступных магазинов")
        return
    db.set_rules(store["key"], min_price=min_price, max_price=max_price, undercut_by=step)
    await update.message.reply_text("Правила обновлены", reply_markup=main_menu())


async def cmd_turbo_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update, context):
        await update.message.reply_text("Доступ запрещен")
        return
    db = _get_db(context)
    store = get_active_store(_get_stores(context), db, update.effective_chat.id)
    if not store:
        await update.message.reply_text("Нет доступных магазинов")
        return
    db.set_settings(store["key"], turbo_mode=True)
    await update.message.reply_text("Турбо включен (30 сек)", reply_markup=main_menu())


async def cmd_turbo_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update, context):
        await update.message.reply_text("Доступ запрещен")
        return
    db = _get_db(context)
    store = get_active_store(_get_stores(context), db, update.effective_chat.id)
    if not store:
        await update.message.reply_text("Нет доступных магазинов")
        return
    db.set_settings(store["key"], turbo_mode=False)
    await update.message.reply_text("Турбо выключен", reply_markup=main_menu())


async def cmd_interval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update, context):
        await update.message.reply_text("Доступ запрещен")
        return
    db = _get_db(context)
    if not context.args:
        await update.message.reply_text("Использование: /interval <sec>")
        return
    store = get_active_store(_get_stores(context), db, update.effective_chat.id)
    if not store:
        await update.message.reply_text("Нет доступных магазинов")
        return
    sec = int(context.args[0])
    db.set_settings(store["key"], poll_interval_seconds=sec)
    await update.message.reply_text(f"Интервал установлен: {sec} сек", reply_markup=main_menu())


async def cmd_exclude_sku(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update, context):
        await update.message.reply_text("Доступ запрещен")
        return
    db = _get_db(context)
    if not context.args:
        await update.message.reply_text("Использование: /exclude_sku <sku1,sku2>")
        return
    store = get_active_store(_get_stores(context), db, update.effective_chat.id)
    if not store:
        await update.message.reply_text("Нет доступных магазинов")
        return
    skus = [s.strip() for s in " ".join(context.args).split(",") if s.strip()]
    db.set_excluded_products(store["key"], skus)
    await update.message.reply_text(f"Исключено товаров: {len(skus)}", reply_markup=main_menu())


async def cmd_run_once(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update, context):
        await update.message.reply_text("Доступ запрещен")
        return
    db = _get_db(context)
    stores = _get_stores(context)
    store = get_active_store(stores, db, update.effective_chat.id)
    if not store:
        await update.message.reply_text("Нет доступных магазинов")
        return
    plan_code, max_skus, paid_active, plan_started_at = db.get_plan(store["key"])
    if not _is_allowed_run(db, update.effective_chat.id, paid_active, store["key"]):
        await update.message.reply_text(tariff_message(), reply_markup=main_menu())
        return
    stats = run_cycle(store, db)
    if stats["offers"] == 0:
        await update.message.reply_text(
            "Нет данных по товарам для синхронизации",
            reply_markup=main_menu(),
        )
        return
    if stats.get("blocked"):
        await update.message.reply_text(
            f"Блок: {stats.get('reason')}\n{tariff_message()}",
            reply_markup=main_menu(),
        )
        return
    db.increment_run_count(update.effective_chat.id, plan_started_at)
    await update.message.reply_text(
        f"Готово: offers={stats['offers']} decisions={stats['decisions']}",
        reply_markup=main_menu(),
    )


# ---------------------------------------------------------------------------
# Callback handler
# ---------------------------------------------------------------------------

async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    db = _get_db(context)
    if not _is_admin(update, context):
        await query.message.reply_text("Доступ запрещен")
        return

    if data == "menu:status":
        await cmd_status(update, context)
        return
    if data == "menu:run_once":
        await cmd_run_once(update, context)
        return
    if data == "menu:stores":
        await cmd_stores(update, context)
        return
    if data == "menu:turbo":
        store = get_active_store(_get_stores(context), db, update.effective_chat.id)
        if not store:
            await query.message.reply_text("Нет доступных магазинов")
            return
        poll_interval, turbo = db.get_settings(store["key"])
        db.set_settings(store["key"], turbo_mode=not turbo)
        await query.message.reply_text(
            f"Турбо {'включен' if not turbo else 'выключен'}",
            reply_markup=main_menu(),
        )
        return
    if data == "menu:rules":
        db.set_pending_action(update.effective_chat.id, "rules")
        await query.message.reply_text(
            "Введите min max step через пробел, например: 2000 10000 150",
            reply_markup=InlineKeyboardMarkup([nav_row()]),
        )
        return
    if data == "menu:exclude_sku":
        db.set_pending_action(update.effective_chat.id, "exclude_sku")
        await query.message.reply_text(
            "Введите SKU через запятую, например: KSP-001,KSP-003",
            reply_markup=InlineKeyboardMarkup([nav_row()]),
        )
        return
    if data == "menu:exclude_competitor":
        db.set_pending_action(update.effective_chat.id, "exclude_competitor")
        await query.message.reply_text(
            "Введите ID конкурентов через запятую, например: C001,C002",
            reply_markup=InlineKeyboardMarkup([nav_row()]),
        )
        return
    if data == "menu:interval":
        db.set_pending_action(update.effective_chat.id, "interval")
        await query.message.reply_text(
            "Введите базовый интервал в секундах, например: 120",
            reply_markup=InlineKeyboardMarkup([nav_row()]),
        )
        return
    if data == "menu:history":
        store = get_active_store(_get_stores(context), db, update.effective_chat.id)
        store_key = store["key"] if store else "default"
        rows = db.get_price_actions(store_key, limit=10)
        if not rows:
            await query.message.reply_text("История пуста", reply_markup=main_menu())
            return
        lines = [f"{r[0]}: {r[1]} -> {r[2]} ({r[3]})" for r in rows]
        await query.message.reply_text("Последние изменения:\n" + "\n".join(lines), reply_markup=main_menu())
        return
    if data == "menu:tariffs":
        await query.message.reply_text(tariff_message(), reply_markup=main_menu())
        return
    if data == "menu:choose_tariff":
        buttons = [
            [InlineKeyboardButton(t["name"], callback_data=f"plan:{t['code']}")]
            for t in _default_tariffs()
        ]
        buttons.append(nav_row())
        await query.message.reply_text("Выберите тариф:", reply_markup=InlineKeyboardMarkup(buttons))
        return
    if data == "menu:scheduler":
        scheduler: Scheduler | None = context.bot_data.get("scheduler")
        if scheduler and scheduler._running:
            buttons = [
                [InlineKeyboardButton("⏹ Остановить", callback_data="sched:stop")],
                nav_row(),
            ]
            await query.message.reply_text("Авто-запуск работает", reply_markup=InlineKeyboardMarkup(buttons))
        else:
            buttons = [
                [InlineKeyboardButton("▶️ Запустить", callback_data="sched:start")],
                nav_row(),
            ]
            await query.message.reply_text("Авто-запуск выключен", reply_markup=InlineKeyboardMarkup(buttons))
        return
    if data == "sched:start":
        scheduler = context.bot_data.get("scheduler")
        if scheduler:
            scheduler.start()
            await query.message.reply_text("Авто-запуск включен", reply_markup=main_menu())
        return
    if data == "sched:stop":
        scheduler = context.bot_data.get("scheduler")
        if scheduler:
            scheduler.stop()
            await query.message.reply_text("Авто-запуск остановлен", reply_markup=main_menu())
        return
    if data.startswith("store:"):
        key = data.split(":", 1)[1]
        db.set_session_store(update.effective_chat.id, key)
        await query.message.reply_text(f"Выбран магазин: {key}", reply_markup=main_menu())
        return
    if data.startswith("plan:"):
        store = get_active_store(_get_stores(context), db, update.effective_chat.id)
        if not store:
            await query.message.reply_text("Нет доступных магазинов")
            return
        code = data.split(":", 1)[1]
        plan = next((p for p in _default_tariffs() if p["code"] == code), None)
        if not plan:
            await query.message.reply_text("Тариф не найден", reply_markup=main_menu())
            return
        db.set_plan(
            store["key"],
            plan["code"],
            int(plan["max_skus"]),
            True,
            datetime.utcnow().isoformat(),
        )
        await query.message.reply_text(f"Тариф выбран: {plan['name']}", reply_markup=main_menu())
        return
    if data == "nav:home":
        await query.message.reply_text("Главное меню", reply_markup=main_menu())
        return
    if data == "nav:back":
        await query.message.reply_text("Главное меню", reply_markup=main_menu())
        return


# ---------------------------------------------------------------------------
# Text input handler
# ---------------------------------------------------------------------------

async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = _get_db(context)
    if not _is_admin(update, context):
        return
    action = db.get_pending_action(update.effective_chat.id)
    if not action:
        return

    text = (update.message.text or "").strip()
    stores = _get_stores(context)

    if action == "rules":
        parts = text.split()
        if len(parts) != 3:
            await update.message.reply_text("Нужно 3 числа: min max step. Пример: 2000 10000 150")
            return
        store = get_active_store(stores, db, update.effective_chat.id)
        if not store:
            await update.message.reply_text("Нет доступных магазинов")
            return
        db.set_rules(store["key"], min_price=float(parts[0]), max_price=float(parts[1]), undercut_by=float(parts[2]))
        db.set_pending_action(update.effective_chat.id, None)
        await update.message.reply_text("Правила обновлены", reply_markup=main_menu())
        return

    if action == "exclude_sku":
        skus = [s.strip() for s in text.split(",") if s.strip()]
        store = get_active_store(stores, db, update.effective_chat.id)
        if not store:
            await update.message.reply_text("Нет доступных магазинов")
            return
        db.set_excluded_products(store["key"], skus)
        db.set_pending_action(update.effective_chat.id, None)
        await update.message.reply_text(f"Исключено товаров: {len(skus)}", reply_markup=main_menu())
        return

    if action == "exclude_competitor":
        comps = [s.strip() for s in text.split(",") if s.strip()]
        store = get_active_store(stores, db, update.effective_chat.id)
        if not store:
            await update.message.reply_text("Нет доступных магазинов")
            return
        db.set_excluded_competitors(store["key"], comps)
        db.set_pending_action(update.effective_chat.id, None)
        await update.message.reply_text(f"Исключено конкурентов: {len(comps)}", reply_markup=main_menu())
        return

    if action == "interval":
        try:
            sec = int(text)
        except ValueError:
            await update.message.reply_text("Введите число, например: 120")
            return
        store = get_active_store(stores, db, update.effective_chat.id)
        if not store:
            await update.message.reply_text("Нет доступных магазинов")
            return
        db.set_settings(store["key"], poll_interval_seconds=sec)
        db.set_pending_action(update.effective_chat.id, None)
        await update.message.reply_text(f"Интервал установлен: {sec} сек", reply_markup=main_menu())
        return


# ---------------------------------------------------------------------------
# Admin commands
# ---------------------------------------------------------------------------

async def cmd_admin_reset_runs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update, context):
        await update.message.reply_text("Доступ запрещен")
        return
    db = _get_db(context)
    target = update.effective_chat.id
    if context.args:
        try:
            target = int(context.args[0])
        except ValueError:
            await update.message.reply_text("Использование: /admin_reset_runs <chat_id>")
            return
    db.reset_run_count(target)
    await update.message.reply_text(f"Пробные запуски сброшены для chat_id={target}")


async def cmd_admin_set_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update, context):
        await update.message.reply_text("Доступ запрещен")
        return
    db = _get_db(context)
    if not context.args:
        await update.message.reply_text("Использование: /admin_set_plan <plan_code>")
        return
    code = context.args[0]
    plan = next((p for p in _default_tariffs() if p["code"] == code), None)
    if not plan:
        await update.message.reply_text("Тариф не найден")
        return
    store = get_active_store(_get_stores(context), db, update.effective_chat.id)
    if not store:
        await update.message.reply_text("Нет доступных магазинов")
        return
    db.set_plan(
        store["key"],
        plan["code"],
        int(plan["max_skus"]),
        True,
        datetime.utcnow().isoformat(),
    )
    await update.message.reply_text(f"Тариф установлен: {plan['name']}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_admins() -> set[int] | None:
    raw = os.getenv("ADMIN_CHAT_IDS", "").strip()
    if not raw:
        return None
    ids = set()
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            ids.add(int(part))
        except ValueError:
            continue
    return ids or None


def _is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    admins = context.bot_data.get("admins")
    if not admins:
        return True
    chat_id = update.effective_chat.id if update.effective_chat else None
    return chat_id in admins


def _default_tariffs() -> list[dict[str, int | str]]:
    return [
        {"code": "start_100", "name": "Start 100", "max_skus": 100, "price_kzt": 1000},
        {"code": "base_500", "name": "Base 500", "max_skus": 500, "price_kzt": 3000},
        {"code": "pro_2000", "name": "Pro 2000", "max_skus": 2000, "price_kzt": 7000},
        {"code": "business_5000", "name": "Business 5000", "max_skus": 5000, "price_kzt": 15000},
        {"code": "enterprise_20000", "name": "Enterprise 20000", "max_skus": 20000, "price_kzt": 30000},
    ]


def tariff_message() -> str:
    lines = ["Тарифы (KZT/мес):"]
    for t in _default_tariffs():
        lines.append(f"- {t['name']}: до {t['max_skus']} товаров — {t['price_kzt']} KZT")
    lines.append("Для апгрейда напишите администратору.")
    return "\n".join(lines)


def _is_allowed_run(db: DB, chat_id: int, paid_active: bool, store_key: str) -> bool:
    if paid_active:
        return True
    _, _, _, plan_started_at = db.get_plan(store_key)
    count = db.get_run_count_checked(chat_id, plan_started_at)
    return count < 5


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN env var")

    db = get_db()

    config_path = os.getenv(
        "MP_BOTS_STORES",
        str(Path(__file__).resolve().parents[3] / "config" / "stores.sample.json"),
    )
    stores = load_stores_from_config(config_path)

    # Also load stores from DB if using Postgres
    db_stores = db.get_stores()
    existing_keys = {s["key"] for s in stores}
    for ds in db_stores:
        if ds["key"] not in existing_keys:
            stores.append(ds)

    scheduler = Scheduler(stores, db)

    app = Application.builder().token(token).build()
    app.bot_data["db"] = db
    app.bot_data["stores"] = stores
    app.bot_data["admins"] = _load_admins()
    app.bot_data["tariffs"] = _default_tariffs()
    app.bot_data["scheduler"] = scheduler

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("stores", cmd_stores))
    app.add_handler(CommandHandler("use", cmd_use))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("rules", cmd_rules))
    app.add_handler(CommandHandler("turbo_on", cmd_turbo_on))
    app.add_handler(CommandHandler("turbo_off", cmd_turbo_off))
    app.add_handler(CommandHandler("interval", cmd_interval))
    app.add_handler(CommandHandler("exclude_sku", cmd_exclude_sku))
    app.add_handler(CommandHandler("run_once", cmd_run_once))
    app.add_handler(CommandHandler("admin_reset_runs", cmd_admin_reset_runs))
    app.add_handler(CommandHandler("admin_set_plan", cmd_admin_set_plan))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    app.run_polling()


if __name__ == "__main__":
    main()
