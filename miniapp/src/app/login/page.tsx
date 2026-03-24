"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

type TelegramWebApp = {
  initData?: string;
};

type TelegramWindow = Window & {
  Telegram?: {
    WebApp?: TelegramWebApp;
  };
};


export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [csrfToken, setCsrfToken] = useState("");
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    fetch("/api/auth/csrf")
      .then((r) => r.json())
      .then((d) => setCsrfToken(String(d?.csrfToken || "")))
      .catch(() => setCsrfToken(""));
  }, []);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-csrf-token": csrfToken },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const data = await res.json();
      setError(data.error || "Ошибка входа");
      return;
    }
    router.push("/dashboard");
  }

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const res = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-csrf-token": csrfToken },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const data = await res.json();
      setError(data.error || "Ошибка регистрации");
      return;
    }
    router.push("/dashboard");
  }

  async function handleTelegramLogin() {
    const tg = (window as TelegramWindow).Telegram?.WebApp;
    if (!tg?.initData) {
      setError("Telegram initData недоступен");
      return;
    }
    const res = await fetch("/api/auth/telegram", {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-csrf-token": csrfToken },
      body: JSON.stringify({ initData: tg.initData }),
    });
    if (!res.ok) {
      const data = await res.json();
      setError(data.error || "Ошибка Telegram входа");
      return;
    }
    router.push("/dashboard");
  }

  return (
    <div className="min-h-screen bg-[#0f1117] text-white">
      <div className="mx-auto flex min-h-screen max-w-xl flex-col justify-center px-6">
        <h1 className="text-3xl font-semibold">Вход в кабинет</h1>
        <p className="mt-2 text-sm text-white/60">
          Войдите через Telegram или используйте email/пароль.
        </p>

        <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-6">
          <button
            onClick={handleTelegramLogin}
            className="w-full rounded-xl bg-[#8ea0ff] px-4 py-2 text-sm font-semibold text-black"
          >
            Войти через Telegram
          </button>
          <div className="my-4 text-center text-xs text-white/40">или</div>
          <form className="space-y-3">
            <input
              className="w-full rounded-xl border border-white/10 bg-black/30 px-3 py-2 text-sm"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <input
              type="password"
              className="w-full rounded-xl border border-white/10 bg-black/30 px-3 py-2 text-sm"
              placeholder="Пароль"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <div className="grid gap-2 md:grid-cols-2">
              <button
                onClick={handleLogin}
                className="rounded-xl bg-white/10 px-4 py-2 text-sm"
              >
                Войти
              </button>
              <button
                onClick={handleRegister}
                className="rounded-xl border border-white/20 px-4 py-2 text-sm"
              >
                Регистрация
              </button>
            </div>
          </form>
          {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
        </div>
      </div>
    </div>
  );
}
