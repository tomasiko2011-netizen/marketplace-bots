import Link from "next/link";

const products = [
  {
    icon: "🦷",
    title: "Стоматологии",
    desc: "Онлайн-запись, напоминания за 24ч и 2ч, no-show -40%",
  },
  {
    icon: "✂️",
    title: "Салоны красоты",
    desc: "Расписание мастеров, запись без звонков, каталог услуг",
  },
  {
    icon: "🚗",
    title: "Автомойки",
    desc: "Запись по времени, уведомление «машина готова»",
  },
  {
    icon: "💪",
    title: "Фитнес-клубы",
    desc: "Расписание, запись на групповые, продление абонемента",
  },
  {
    icon: "👗",
    title: "Магазины одежды",
    desc: "Каталог с фото, размерами и ценами, заказ в чате",
  },
  {
    icon: "🎂",
    title: "Пекарни",
    desc: "Предзаказ тортов, надписи, детали — без ошибок",
  },
  {
    icon: "🐾",
    title: "Ветклиники",
    desc: "Запись на приём, напоминания о прививках по графику",
  },
  {
    icon: "🍷",
    title: "Рестораны",
    desc: "Бронирование с предоплатой, меню, напоминания",
  },
];

const stats = [
  { value: "316", label: "компаний в системе" },
  { value: "10+", label: "готовых продуктов" },
  { value: "10", label: "городов Казахстана" },
  { value: "24/7", label: "бот работает" },
];

const portfolio = [
  { name: "SkladPro", desc: "ERP/WMS для склада и торговли", url: "https://skladpro.xn--80adbie4ccpo.kz", tag: "ERP" },
  { name: "Интернет-магазин", desc: "Zara-стиль, каталог, корзина", url: "https://shop.truest.kz", tag: "E-commerce" },
  { name: "Оптовый склад", desc: "Учёт одежды, POS, PWA", url: "https://opt.truest.kz", tag: "Склад" },
  { name: "RestoBooking", desc: "Бронирование, 73 ресторана", url: "https://restobooking.vercel.app", tag: "HoReCa" },
  { name: "Халык Контроль", desc: "Мониторинг цен СЗПТ", url: "https://halyk.truest.kz", tag: "GovTech" },
  { name: "Отель", desc: "Управление гостиницей", url: "https://hotel.truest.kz", tag: "Hospitality" },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      {/* Nav */}
      <nav className="sticky top-0 z-50 border-b border-white/5 bg-[#0a0a0f]/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 text-sm font-bold">T</div>
            <span className="text-lg font-semibold">TruEst Digital</span>
          </div>
          <div className="hidden gap-6 text-sm text-white/60 md:flex">
            <a href="#solutions" className="hover:text-white transition">Решения</a>
            <a href="#portfolio" className="hover:text-white transition">Портфолио</a>
            <a href="#pricing" className="hover:text-white transition">Цены</a>
            <a href="#contact" className="hover:text-white transition">Контакты</a>
          </div>
          <a href="https://wa.me/77010770199" target="_blank" className="rounded-full bg-green-500 px-4 py-2 text-sm font-semibold text-white hover:bg-green-400 transition">
            WhatsApp
          </a>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-blue-600/10 via-transparent to-transparent" />
        <div className="mx-auto max-w-6xl px-6 pb-20 pt-24 text-center">
          <div className="mb-4 inline-block rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-1 text-xs text-blue-400">
            Автоматизация для малого бизнеса Казахстана
          </div>
          <h1 className="mx-auto max-w-4xl text-4xl font-bold leading-tight md:text-6xl">
            WhatsApp-боты, которые{" "}
            <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              работают за вас
            </span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-white/60">
            Клиенты записываются, заказывают и бронируют через WhatsApp — 24/7, без звонков, без пропущенных заявок. Вы получаете готовые заказы.
          </p>
          <div className="mt-8 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
            <a href="https://wa.me/77010770199?text=Здравствуйте!%20Хочу%20демо%20WhatsApp-бота" target="_blank"
              className="rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 px-8 py-3 text-base font-semibold shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 transition">
              Получить демо за 3 минуты
            </a>
            <a href="#solutions"
              className="rounded-xl border border-white/20 px-8 py-3 text-base text-white/80 hover:border-white/40 transition">
              Смотреть решения
            </a>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="border-y border-white/5 bg-white/[0.02]">
        <div className="mx-auto grid max-w-6xl grid-cols-2 gap-8 px-6 py-12 md:grid-cols-4">
          {stats.map((s) => (
            <div key={s.label} className="text-center">
              <div className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">{s.value}</div>
              <div className="mt-1 text-sm text-white/50">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Solutions */}
      <section id="solutions" className="mx-auto max-w-6xl px-6 py-20">
        <div className="text-center">
          <h2 className="text-3xl font-bold md:text-4xl">Готовые решения для 8 ниш</h2>
          <p className="mt-3 text-white/50">Каждый бот настроен под специфику вашей отрасли</p>
        </div>
        <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {products.map((p) => (
            <div key={p.title} className="group rounded-2xl border border-white/5 bg-white/[0.02] p-6 hover:border-blue-500/30 hover:bg-blue-500/5 transition-all duration-300">
              <div className="text-3xl">{p.icon}</div>
              <h3 className="mt-3 text-lg font-semibold">{p.title}</h3>
              <p className="mt-2 text-sm text-white/50 leading-relaxed">{p.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="border-y border-white/5 bg-white/[0.02]">
        <div className="mx-auto max-w-6xl px-6 py-20">
          <h2 className="text-center text-3xl font-bold">Как это работает</h2>
          <div className="mt-12 grid gap-8 md:grid-cols-3">
            {[
              { step: "01", title: "Клиент пишет в WhatsApp", desc: "Открывает чат с вашим номером — бот мгновенно отвечает" },
              { step: "02", title: "Бот показывает услуги", desc: "Расписание, цены, свободное время — всё автоматически" },
              { step: "03", title: "Вы получаете заявку", desc: "Готовый заказ/запись приходит вам. Без звонков и ожидания" },
            ].map((item) => (
              <div key={item.step} className="relative rounded-2xl border border-white/5 bg-white/[0.02] p-8">
                <div className="text-5xl font-bold text-white/5">{item.step}</div>
                <h3 className="mt-2 text-lg font-semibold">{item.title}</h3>
                <p className="mt-2 text-sm text-white/50">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Portfolio */}
      <section id="portfolio" className="mx-auto max-w-6xl px-6 py-20">
        <h2 className="text-center text-3xl font-bold">Портфолио</h2>
        <p className="mt-3 text-center text-white/50">10+ живых проектов на production</p>
        <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {portfolio.map((p) => (
            <a key={p.name} href={p.url} target="_blank" rel="noopener"
              className="group rounded-2xl border border-white/5 bg-white/[0.02] p-6 hover:border-purple-500/30 transition-all duration-300">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">{p.name}</h3>
                <span className="rounded-full border border-white/10 px-2 py-0.5 text-xs text-white/40">{p.tag}</span>
              </div>
              <p className="mt-2 text-sm text-white/50">{p.desc}</p>
              <div className="mt-4 text-xs text-blue-400 opacity-0 group-hover:opacity-100 transition">Открыть сайт →</div>
            </a>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="border-y border-white/5 bg-white/[0.02]">
        <div className="mx-auto max-w-6xl px-6 py-20">
          <h2 className="text-center text-3xl font-bold">Цены</h2>
          <p className="mt-3 text-center text-white/50">Прозрачно, без скрытых платежей</p>
          <div className="mt-12 grid gap-6 md:grid-cols-3">
            {[
              {
                name: "WhatsApp-бот",
                price: "50 000",
                period: "разовая настройка",
                monthly: "+ 10 000 ₸/мес",
                features: ["Запись / каталог / бронь", "Работает 24/7", "Напоминания клиентам", "Аналитика заявок"],
                cta: "Заказать бота",
                popular: false,
              },
              {
                name: "ERP Товаровед",
                price: "5 000",
                period: "₸/мес",
                monthly: "от 5 000 ₸/мес",
                features: ["Склад и продажи", "Документооборот", "Аналитика и отчёты", "Multi-tenant, 5 ролей"],
                cta: "Попробовать",
                popular: true,
              },
              {
                name: "Сайт под ключ",
                price: "100 000",
                period: "от",
                monthly: "хостинг бесплатно",
                features: ["Лендинг или магазин", "Мобильная адаптация", "SEO оптимизация", "Админ-панель"],
                cta: "Обсудить проект",
                popular: false,
              },
            ].map((plan) => (
              <div key={plan.name}
                className={`relative rounded-2xl border p-8 ${plan.popular ? "border-blue-500/50 bg-blue-500/5" : "border-white/5 bg-white/[0.02]"}`}>
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-blue-500 px-3 py-0.5 text-xs font-semibold">
                    Популярный
                  </div>
                )}
                <h3 className="text-lg font-semibold">{plan.name}</h3>
                <div className="mt-4">
                  <span className="text-4xl font-bold">{plan.price}</span>
                  <span className="ml-1 text-sm text-white/50">{plan.period}</span>
                </div>
                <p className="mt-1 text-xs text-white/40">{plan.monthly}</p>
                <ul className="mt-6 space-y-3">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-center gap-2 text-sm text-white/70">
                      <span className="text-green-400">✓</span> {f}
                    </li>
                  ))}
                </ul>
                <a href="https://wa.me/77010770199" target="_blank"
                  className={`mt-8 block rounded-xl py-3 text-center text-sm font-semibold transition ${plan.popular
                    ? "bg-blue-500 hover:bg-blue-400"
                    : "border border-white/20 hover:border-white/40"
                  }`}>
                  {plan.cta}
                </a>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact */}
      <section id="contact" className="mx-auto max-w-6xl px-6 py-20 text-center">
        <h2 className="text-3xl font-bold">Готовы автоматизировать бизнес?</h2>
        <p className="mt-3 text-white/50">Напишите — покажем демо за 3 минуты</p>
        <div className="mt-8 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <a href="https://wa.me/77010770199?text=Здравствуйте!%20Хочу%20узнать%20подробнее" target="_blank"
            className="flex items-center gap-2 rounded-xl bg-green-500 px-8 py-3 text-base font-semibold hover:bg-green-400 transition">
            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
            Написать в WhatsApp
          </a>
          <a href="tel:+77010770199"
            className="rounded-xl border border-white/20 px-8 py-3 text-base text-white/80 hover:border-white/40 transition">
            +7 701 077 01 99
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 bg-white/[0.02]">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 py-8 md:flex-row">
          <div className="flex items-center gap-2">
            <div className="flex h-6 w-6 items-center justify-center rounded bg-gradient-to-br from-blue-500 to-purple-600 text-xs font-bold">T</div>
            <span className="text-sm font-semibold">TruEst Digital</span>
          </div>
          <p className="text-xs text-white/30">Тараз, Казахстан — Цифровизация малого бизнеса</p>
          <div className="flex gap-4 text-sm text-white/40">
            <a href="https://t.me/TruestDigital" target="_blank" className="hover:text-white transition">Telegram</a>
            <a href="https://wa.me/77010770199" target="_blank" className="hover:text-white transition">WhatsApp</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
