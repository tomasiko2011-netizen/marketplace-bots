import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-[#0f1117] text-white">
      <div className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-6">
        <p className="text-xs uppercase tracking-[0.2em] text-[#8ea0ff]">skladprobot</p>
        <h1 className="mt-3 text-4xl font-semibold">Панель управления</h1>
        <p className="mt-3 max-w-xl text-sm text-white/60">
          Управляйте демпинг‑ботом, тарифами и автозапусками через личный кабинет.
        </p>
        <div className="mt-6 flex gap-3">
          <Link
            href="/login"
            className="rounded-xl bg-[#8ea0ff] px-4 py-2 text-sm font-semibold text-black"
          >
            Войти
          </Link>
          <Link
            href="/dashboard"
            className="rounded-xl border border-white/20 px-4 py-2 text-sm text-white/80"
          >
            Кабинет
          </Link>
        </div>
      </div>
    </div>
  );
}
