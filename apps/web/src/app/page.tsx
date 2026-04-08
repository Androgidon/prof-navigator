const features = [
  {
    title: "Explainable рекомендации",
    description:
      "Rule-based движок со взвешенными сигналами профиля, интересов и региона делает результат прозрачным.",
  },
  {
    title: "Тест 30+ вопросов",
    description:
      "Блоковая структура, сохранение прогресса и возобновление обеспечивают комфортное прохождение на любом устройстве.",
  },
  {
    title: "Практичные карточки",
    description:
      "Каждая профессия содержит описание, предметы, навыки и конкретные шаги ≪что делать прямо сейчас≫.",
  },
];

const metrics = [
  { label: "Top профессий", value: "10–15" },
  { label: "Вопросов", value: "30–35" },
  { label: "Влияние", value: "Explainability + trust" },
];

const principles = [
  "Explainability first",
  "Trust first",
  "Actionability",
  "Simple before smart",
  "Curated before scale",
];

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      <main className="mx-auto flex min-h-screen max-w-6xl flex-col gap-12 px-6 py-16">
        <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-slate-900/80 to-slate-700/80 p-10 shadow-2xl">
          <div className="flex flex-col gap-8 lg:flex-row lg:items-center lg:justify-between">
            <div className="max-w-2xl space-y-6">
              <p className="text-sm uppercase tracking-[0.4em] text-slate-400">
                CareerPath MVP
              </p>
              <h1 className="text-4xl font-semibold leading-tight text-white md:text-5xl">
                Профориентационный навигатор для школьников и абитуриентов
              </h1>
              <p className="text-lg text-slate-300">
                Понимай себя, проходи тест, получай explainable рекомендации и изучай карточки профессий с
                маршрутом действий и сигналы прозрачности.
              </p>
              <div className="flex flex-wrap gap-3">
                <a
                  href="/register"
                  className="rounded-full border border-amber-400/70 bg-amber-400/10 px-6 py-3 text-sm font-semibold uppercase tracking-wide text-amber-200 transition hover:border-amber-300 hover:bg-amber-400/30"
                >
                  Пройти тест
                </a>
                <a
                  href="/dashboard"
                  className="rounded-full border border-white/20 px-6 py-3 text-sm font-semibold uppercase tracking-wide text-white transition hover:border-white hover:bg-white/10"
                >
                  Личный кабинет
                </a>
              </div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-lg">
              <p className="text-sm uppercase tracking-wider text-slate-400">Результат</p>
              <h2 className="text-3xl font-semibold text-white">87% соответствие</h2>
              <p className="text-sm text-slate-300">
                Объяснение: психология + оценки + интересы + региональный бонус.
              </p>
            </div>
          </div>
        </section>

        <section className="grid gap-6 md:grid-cols-3">
          {metrics.map((metric) => (
            <article
              key={metric.label}
              className="rounded-2xl border border-white/10 bg-slate-900/70 p-6 text-center shadow-lg"
            >
              <p className="text-sm uppercase tracking-[0.5em] text-slate-400">{metric.label}</p>
              <p className="mt-4 text-3xl font-semibold text-white">{metric.value}</p>
            </article>
          ))}
        </section>

        <section className="grid gap-6 md:grid-cols-3">
          {features.map((feature) => (
            <article
              key={feature.title}
              className="flex h-full flex-col gap-4 rounded-3xl border border-white/10 bg-gradient-to-br from-slate-900/80 to-slate-900/20 p-6"
            >
              <h3 className="text-xl font-semibold text-white">{feature.title}</h3>
              <p className="text-sm leading-relaxed text-slate-300">{feature.description}</p>
            </article>
          ))}
        </section>

        <section className="rounded-3xl border border-white/10 bg-slate-900/80 p-8">
          <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.4em] text-amber-400">Основные принципы</p>
              <h2 className="text-3xl font-semibold text-white">Продуктовая и инженерная дисциплина</h2>
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm text-slate-300 md:grid-cols-3">
              {principles.map((principle) => (
                <span key={principle} className="rounded-2xl border border-white/10 px-4 py-2 text-center">
                  {principle}
                </span>
              ))}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
