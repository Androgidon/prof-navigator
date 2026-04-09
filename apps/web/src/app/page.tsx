import Link from "next/link";
import { SiteHeader } from "@/components/layout/site-header";
import { HeroSection } from "@/components/layout/hero-section";
import { FeatureCard } from "@/components/layout/feature-card";
import { StepCard } from "@/components/layout/step-card";
import { TrustPanel } from "@/components/layout/trust-panel";
import { CTASection } from "@/components/layout/cta-section";
import { SiteFooter } from "@/components/layout/site-footer";

const features = [
  {
    title: "Точные рекомендации",
    description:
      "Научно обоснованный тест подбирает профессии и объясняет, какие предметы и навыки нужно развивать.",
    icon: "🎯",
  },
  {
    title: "Прозрачные объяснения",
    description:
      "Каждая профессия сопровождается факторами доверия: профиль, интересы, оценки и региональные сигналы.",
    icon: "💡",
  },
  {
    title: "Практические советы",
    description:
      "Наставления по тому, что делать после теста: курсы, проекты и способы попробовать профессию прямо сейчас.",
    icon: "🚀",
  },
];

const steps = [
  {
    number: 1,
    title: "Создай профиль",
    description: "Укажи свои интересы, любимые предметы и вид деятельности.",
  },
  {
    number: 2,
    title: "Пройди тест",
    description: "Ответь на 30–35 вопросов о своих способностях и предпочтениях.",
  },
  {
    number: 3,
    title: "Получи результаты",
    description: "Система рассчитает твой профиль и покажет ключевые сильные стороны.",
  },
  {
    number: 4,
    title: "Изучи профессии",
    description: "Узнай, какие профессии подходят, почему именно они и что делать дальше.",
  },
];

const trustItems = [
  "Без регистрации для прохождения",
  "Полностью бесплатно",
  "Данные защищены",
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      <SiteHeader />

      <main className="landing-shell">
        <HeroSection
          badge="Бесплатный профориентационный тест"
          title="Найди свой путь в"
          titleAccent="будущее"
          subtitle="Пройди тест и получи персонализированные рекомендации по профессиям, которые подходят именно тебе."
        >
          <div className="hero-cta">
            <Link href="/register" className="header-btn header-btn-primary">
              Начать тест бесплатно
            </Link>
            <Link href="#how-it-works" className="header-btn header-btn-ghost">
              Как это работает
            </Link>
          </div>
        </HeroSection>

        <section className="feature-section">
          <h2>Почему CareerPath?</h2>
          <p>Мы помогаем старшеклассникам и абитуриентам принимать осознанные решения о будущем.</p>
          <div className="feature-grid">
            {features.map((feature) => (
              <FeatureCard
                key={feature.title}
                icon={<span className="feature-icon-emoji">{feature.icon}</span>}
                title={feature.title}
                description={feature.description}
              />
            ))}
          </div>
        </section>

        <section id="how-it-works" className="how-it-works-section">
          <h2>Как это работает</h2>
          <p>Три простых шага к осознанному выбору профессии</p>
          <div className="steps-grid">
            {steps.map((step) => (
              <StepCard
                key={step.number}
                number={step.number}
                title={step.title}
                description={step.description}
              />
            ))}
          </div>
        </section>

        <TrustPanel
          title="Мы заботимся о конфиденциальности"
          description="Все данные защищены и используются только для персонализированных рекомендаций. Мы никогда не передаём информацию третьим сторонам."
          items={trustItems}
        />

        <CTASection
          title="Готов узнать своё будущее?"
          description="Начни тест сейчас и получи explainable рекомендации с дорожной картой."
          action={
            <Link href="/register" className="header-btn header-btn-primary">
              Начать тест бесплатно →
            </Link>
          }
        />
      </main>

      <SiteFooter />
    </div>
  );
}