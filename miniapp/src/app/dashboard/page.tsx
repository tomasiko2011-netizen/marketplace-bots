"use client";

import { useEffect, useState } from "react";

type Store = {
  store_key: string;
  title: string;
  marketplace: string;
  poll_interval_seconds: number;
  turbo_mode: boolean;
  plan_code: string;
  max_skus: number;
  paid_active: boolean;
  offer_count: number;
};

type PriceAction = {
  sku: string;
  old_price: number;
  new_price: number;
  reason: string;
  created_at: string;
};

type Tariff = {
  code: string;
  name: string;
  max_skus: number;
  price_kzt: number;
};

type StoreDetail = {
  settings: {
    poll_interval_seconds: number;
    turbo_mode: boolean;
    plan_code: string;
    max_skus: number;
    paid_active: boolean;
  } | null;
  rules: { min_price: number | null; max_price: number | null; undercut_by: number | null }[];
  history: PriceAction[];
  excludedSkus: string[];
  excludedCompetitors: string[];
};

type DashboardData = {
  stores: Store[];
  recentActions: PriceAction[];
  tariffs: Tariff[];
  trialRunsUsed: number;
  trialRunsLimit: number;
};

function fmtMoney(v: number) {
  return new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 0 }).format(v) + " ₸";
}

function Badge({ active, label }: { active: boolean; label: string }) {
  return (
    <span
      className={`rounded-full px-2 py-0.5 text-xs font-medium ${
        active ? "bg-green-500/20 text-green-400" : "bg-yellow-500/20 text-yellow-400"
      }`}
    >
      {label}
    </span>
  );
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedStore, setSelectedStore] = useState<string | null>(null);
  const [detail, setDetail] = useState<StoreDetail | null>(null);
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState<string | null>(null);

  // editable fields
  const [editInterval, setEditInterval] = useState("");
  const [editTurbo, setEditTurbo] = useState(false);
  const [editMin, setEditMin] = useState("");
  const [editMax, setEditMax] = useState("");
  const [editStep, setEditStep] = useState("");
  const [editExSkus, setEditExSkus] = useState("");
  const [editExComps, setEditExComps] = useState("");

  async function loadOverview() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/dashboard/overview", { cache: "no-store" });
      if (!res.ok) throw new Error("Failed");
      const d = (await res.json()) as DashboardData;
      setData(d);
      if (!selectedStore && d.stores.length > 0) {
        setSelectedStore(d.stores[0].store_key);
      }
    } catch {
      setError("Не удалось загрузить данные");
    } finally {
      setLoading(false);
    }
  }

  async function loadStoreDetail(storeKey: string) {
    try {
      const res = await fetch(`/api/dashboard/settings?store=${encodeURIComponent(storeKey)}`, {
        cache: "no-store",
      });
      if (!res.ok) return;
      const d = (await res.json()) as StoreDetail;
      setDetail(d);
      setEditInterval(String(d.settings?.poll_interval_seconds ?? 120));
      setEditTurbo(d.settings?.turbo_mode ?? false);
      const rule = d.rules?.[0];
      setEditMin(rule?.min_price != null ? String(rule.min_price) : "");
      setEditMax(rule?.max_price != null ? String(rule.max_price) : "");
      setEditStep(rule?.undercut_by != null ? String(rule.undercut_by) : "");
      setEditExSkus(d.excludedSkus?.join(", ") ?? "");
      setEditExComps(d.excludedCompetitors?.join(", ") ?? "");
    } catch {
      setDetail(null);
    }
  }

  useEffect(() => {
    void loadOverview();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (selectedStore) void loadStoreDetail(selectedStore);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedStore]);

  async function handleSave() {
    if (!selectedStore) return;
    setSaving(true);
    setSaveMsg(null);
    try {
      await fetch("/api/dashboard/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          store_key: selectedStore,
          settings: {
            poll_interval_seconds: Number(editInterval) || 120,
            turbo_mode: editTurbo,
          },
          rule: {
            min_price: editMin ? Number(editMin) : null,
            max_price: editMax ? Number(editMax) : null,
            undercut_by: editStep ? Number(editStep) : null,
          },
          excluded_skus: editExSkus,
          excluded_competitors: editExComps,
        }),
      });
      setSaveMsg("Сохранено");
      await Promise.all([loadStoreDetail(selectedStore), loadOverview()]);
      setTimeout(() => setSaveMsg(null), 2000);
    } finally {
      setSaving(false);
    }
  }

  async function handleSelectTariff(code: string) {
    if (!selectedStore) return;
    setSaving(true);
    const plan = data?.tariffs.find((t) => t.code === code);
    if (!plan) return;
    try {
      await fetch("/api/dashboard/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          store_key: selectedStore,
          settings: {
            plan_code: plan.code,
            max_skus: plan.max_skus,
            paid_active: true,
          },
        }),
      });
      setSaveMsg(`Тариф ${plan.name} выбран`);
      await Promise.all([loadStoreDetail(selectedStore), loadOverview()]);
      setTimeout(() => setSaveMsg(null), 2000);
    } finally {
      setSaving(false);
    }
  }

  const activeStore = data?.stores.find((s) => s.store_key === selectedStore);

  return (
    <div className="min-h-screen bg-[#0f1117] text-white">
      <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-[#8ea0ff]">skladprobot</p>
            <h1 className="mt-1 text-2xl font-semibold">Панель управления</h1>
          </div>
          <button
            onClick={loadOverview}
            className="rounded-xl border border-white/20 px-4 py-2 text-sm hover:bg-white/10"
          >
            Обновить
          </button>
        </div>

        {saveMsg && (
          <div className="mt-3 rounded-xl border border-green-500/30 bg-green-500/10 px-4 py-2 text-sm text-green-300">
            {saveMsg}
          </div>
        )}

        {loading && (
          <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-5 text-sm text-white/70">
            Загрузка...
          </div>
        )}

        {error && (
          <div className="mt-6 rounded-2xl border border-red-400/30 bg-red-500/10 p-5 text-sm text-red-200">
            {error}
          </div>
        )}

        {data && (
          <>
            {/* Trial banner */}
            {!activeStore?.paid_active && (
              <div className="mt-4 rounded-xl border border-yellow-500/30 bg-yellow-500/10 px-4 py-3 text-sm text-yellow-200">
                Пробный режим: использовано {data.trialRunsUsed} / {data.trialRunsLimit} запусков
              </div>
            )}

            {/* Store tabs */}
            {data.stores.length > 0 && (
              <div className="mt-6 flex gap-2 overflow-x-auto">
                {data.stores.map((s) => (
                  <button
                    key={s.store_key}
                    onClick={() => setSelectedStore(s.store_key)}
                    className={`whitespace-nowrap rounded-xl px-4 py-2 text-sm ${
                      selectedStore === s.store_key
                        ? "bg-[#8ea0ff] font-semibold text-black"
                        : "border border-white/20 hover:bg-white/10"
                    }`}
                  >
                    {s.title || s.store_key}
                  </button>
                ))}
              </div>
            )}

            {data.stores.length === 0 && (
              <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-6 text-center text-sm text-white/60">
                Нет подключённых магазинов. Добавьте магазин через Telegram-бот.
              </div>
            )}

            {/* Store detail */}
            {activeStore && (
              <div className="mt-4 grid gap-4 lg:grid-cols-2">
                {/* Status card */}
                <section className="rounded-2xl border border-white/10 bg-white/5 p-5">
                  <h2 className="text-sm font-semibold text-white/90">Статус</h2>
                  <div className="mt-3 space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-white/60">Маркетплейс</span>
                      <span className="capitalize">{activeStore.marketplace}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/60">Товаров</span>
                      <span>{activeStore.offer_count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/60">Интервал</span>
                      <span>{activeStore.poll_interval_seconds} сек</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/60">Турбо</span>
                      <Badge active={activeStore.turbo_mode} label={activeStore.turbo_mode ? "ON" : "OFF"} />
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/60">Тариф</span>
                      <span>
                        {activeStore.plan_code}{" "}
                        <Badge active={activeStore.paid_active} label={activeStore.paid_active ? "оплачен" : "trial"} />
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/60">Лимит SKU</span>
                      <span>{activeStore.max_skus}</span>
                    </div>
                  </div>
                </section>

                {/* Settings form */}
                <section className="rounded-2xl border border-white/10 bg-white/5 p-5">
                  <h2 className="text-sm font-semibold text-white/90">Настройки</h2>
                  <div className="mt-3 space-y-3">
                    <div className="flex items-center gap-3">
                      <label className="flex-1 block">
                        <span className="text-xs text-white/60">Интервал (сек)</span>
                        <input
                          type="number"
                          value={editInterval}
                          onChange={(e) => setEditInterval(e.target.value)}
                          className="mt-1 w-full rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-sm"
                        />
                      </label>
                      <label className="flex items-center gap-2 pt-4">
                        <input
                          type="checkbox"
                          checked={editTurbo}
                          onChange={(e) => setEditTurbo(e.target.checked)}
                          className="h-4 w-4 rounded border-white/20 bg-black/30"
                        />
                        <span className="text-xs text-white/60">Турбо (30с)</span>
                      </label>
                    </div>
                    <div className="grid grid-cols-3 gap-2">
                      <label className="block">
                        <span className="text-xs text-white/60">Мин. цена</span>
                        <input
                          type="number"
                          value={editMin}
                          onChange={(e) => setEditMin(e.target.value)}
                          className="mt-1 w-full rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-sm"
                          placeholder="—"
                        />
                      </label>
                      <label className="block">
                        <span className="text-xs text-white/60">Макс. цена</span>
                        <input
                          type="number"
                          value={editMax}
                          onChange={(e) => setEditMax(e.target.value)}
                          className="mt-1 w-full rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-sm"
                          placeholder="—"
                        />
                      </label>
                      <label className="block">
                        <span className="text-xs text-white/60">Шаг (undercut)</span>
                        <input
                          type="number"
                          value={editStep}
                          onChange={(e) => setEditStep(e.target.value)}
                          className="mt-1 w-full rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-sm"
                          placeholder="—"
                        />
                      </label>
                    </div>
                    <label className="block">
                      <span className="text-xs text-white/60">Исключённые SKU (через запятую)</span>
                      <input
                        type="text"
                        value={editExSkus}
                        onChange={(e) => setEditExSkus(e.target.value)}
                        className="mt-1 w-full rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-sm"
                        placeholder="KSP-001, KSP-003"
                      />
                    </label>
                    <label className="block">
                      <span className="text-xs text-white/60">Исключённые конкуренты (через запятую)</span>
                      <input
                        type="text"
                        value={editExComps}
                        onChange={(e) => setEditExComps(e.target.value)}
                        className="mt-1 w-full rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-sm"
                        placeholder="C001, C002"
                      />
                    </label>
                    <button
                      onClick={handleSave}
                      disabled={saving}
                      className="w-full rounded-xl bg-[#8ea0ff] px-4 py-2 text-sm font-semibold text-black disabled:opacity-50"
                    >
                      {saving ? "Сохранение..." : "Сохранить"}
                    </button>
                  </div>
                </section>
              </div>
            )}

            {/* Price history */}
            {detail && detail.history.length > 0 && (
              <section className="mt-4 rounded-2xl border border-white/10 bg-white/5 p-5">
                <h2 className="text-sm font-semibold text-white/90">История изменений цен</h2>
                <div className="mt-3 overflow-x-auto">
                  <table className="min-w-full text-left text-sm">
                    <thead className="text-white/60">
                      <tr>
                        <th className="py-2 pr-4">SKU</th>
                        <th className="py-2 pr-4">Было</th>
                        <th className="py-2 pr-4">Стало</th>
                        <th className="py-2 pr-4">Причина</th>
                        <th className="py-2">Время</th>
                      </tr>
                    </thead>
                    <tbody>
                      {detail.history.map((a, i) => (
                        <tr key={i} className="border-t border-white/10">
                          <td className="py-2 pr-4 font-mono text-xs">{a.sku}</td>
                          <td className="py-2 pr-4">{fmtMoney(a.old_price)}</td>
                          <td className="py-2 pr-4">{fmtMoney(a.new_price)}</td>
                          <td className="py-2 pr-4 text-white/60">{a.reason}</td>
                          <td className="py-2 text-white/50 text-xs">
                            {new Date(a.created_at).toLocaleString("ru-RU")}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            )}

            {/* Tariffs */}
            {data.tariffs.length > 0 && (
              <section className="mt-4 rounded-2xl border border-white/10 bg-white/5 p-5">
                <h2 className="text-sm font-semibold text-white/90">Тарифы</h2>
                <div className="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-5">
                  {data.tariffs.map((t) => {
                    const isCurrent = activeStore?.plan_code === t.code;
                    return (
                      <button
                        key={t.code}
                        onClick={() => !isCurrent && handleSelectTariff(t.code)}
                        disabled={saving}
                        className={`rounded-xl border p-3 text-center transition ${
                          isCurrent
                            ? "border-[#8ea0ff]/50 bg-[#8ea0ff]/10 cursor-default"
                            : "border-white/10 hover:border-[#8ea0ff]/30 hover:bg-white/5 cursor-pointer"
                        } disabled:opacity-50`}
                      >
                        <p className="text-sm font-semibold">{t.name}</p>
                        <p className="mt-1 text-xs text-white/60">до {t.max_skus} SKU</p>
                        <p className="mt-1 text-sm">{fmtMoney(t.price_kzt)}/мес</p>
                        {isCurrent && (
                          <span className="mt-1 inline-block text-xs text-[#8ea0ff]">текущий</span>
                        )}
                      </button>
                    );
                  })}
                </div>
              </section>
            )}
          </>
        )}
      </div>
    </div>
  );
}
