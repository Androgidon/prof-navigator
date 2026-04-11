"use client";

import Link from "next/link";
import { useState, type ReactNode } from "react";
import { SiteHeader } from "@/components/layout/site-header";
import { HeroSection } from "@/components/layout/hero-section";
import { FeatureCard } from "@/components/layout/feature-card";
import { StepCard } from "@/components/layout/step-card";
import { TrustPanel } from "@/components/layout/trust-panel";
import { CTASection } from "@/components/layout/cta-section";
import { SiteFooter } from "@/components/layout/site-footer";
import { getTestEntryRoute } from "@/lib/auth-flow";

const features: { title: string; description: string; icon: ReactNode }[] = [
  {
    title: "Точные рекомендации",
    description:
      "Научно обоснованный тест подбирает профессии и объясняет, какие предметы и навыки нужно развивать.",
    icon: (
      <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
        <circle cx="12" cy="12" r="9" />
        <circle cx="12" cy="12" r="5" />
        <circle cx="12" cy="12" r="1.5" />
      </svg>
    ),
  },
  {
    title: "Прозрачные объяснения",
    description:
      "Каждая профессия сопровождается факторами доверия: профиль, интересы, оценки и региональные сигналы.",
    icon: (
      <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
        <path d="M9 18h6" />
        <path d="M10 22h4" />
        <path d="M12 2a7 7 0 0 0-4 12.8V17h8v-2.2A7 7 0 0 0 12 2z" />
      </svg>
    ),
  },
  {
    title: "Практические советы",
    description:
      "Наставления по тому, что делать после теста: курсы, проекты и способы попробовать профессию прямо сейчас.",
    icon: (
      <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
        <path d="M5 19c3-1 4-2 5-5" />
        <path d="M14 10l6-6" />
        <path d="M13 3h8v8" />
      </svg>
    ),
  },
];

const steps: { number: number; title: string; description: string; icon: ReactNode }[] = [
  {
    number: 1,
    title: "Создай профиль",
    description: "Расскажи о себе, своих интересах и сильных предметах",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
        <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
        <circle cx="8.5" cy="7" r="4" />
        <line x1="20" y1="8" x2="20" y2="14" />
        <line x1="23" y1="11" x2="17" y2="11" />
      </svg>
    ),
  },
  {
    number: 2,
    title: "Пройди тест",
    description: "Ответь на вопросы о своих предпочтениях и склонностях (15-20 минут)",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
        <rect x="8" y="2" width="8" height="4" rx="1" />
        <path d="M9 4H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-3" />
        <line x1="9" y1="12" x2="15" y2="12" />
        <line x1="9" y1="16" x2="15" y2="16" />
      </svg>
    ),
  },
  {
    number: 3,
    title: "Получи результаты",
    description: "Узнай, какие профессии тебе подходят и почему",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
        <path d="M12 3v5" />
        <path d="M7 8h3" />
        <path d="M14 8h3" />
        <path d="M4 14h4l2 6 4-12 2 6h4" />
      </svg>
    ),
  },
  {
    number: 4,
    title: "Изучи профессии",
    description: "Подробно узнай о каждой профессии, зарплатах и путях развития",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
        <path d="M3 5a2 2 0 0 1 2-2h5v17H5a2 2 0 0 0-2 2V5z" />
        <path d="M21 5a2 2 0 0 0-2-2h-5v17h5a2 2 0 0 1 2 2V5z" />
      </svg>
    ),
  },
];

const trustItems = [
  "Полностью бесплатно",
  "Без регистрации для теста",
  "Научный подход",
];

export default function HomePage() {
  const [testEntryHref] = useState<"/login" | "/onboarding" | "/test">(() => {
    if (typeof window === "undefined") {
      return "/login";
    }
    return getTestEntryRoute();
  });

  return (
    <div className="min-h-screen bg-background">
      <SiteHeader />

      <main className="landing-shell">
        <HeroSection
          badge={<><span aria-hidden>✧</span> Бесплатный профориентационный тест</>}
          title="Найди свой путь"
          titleAccent="в будущее"
          subtitle="Пройди тест и получи персонализированные рекомендации по профессиям, которые подходят именно тебе"
        >
          <div className="hero-cta">
              <Link href={testEntryHref} className="header-btn header-btn-primary">
                Начать тест <span aria-hidden>→</span>
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
                icon={feature.icon}
                title={feature.title}
                description={feature.description}
              />
            ))}
          </div>
        </section>

        <section id="how-it-works" className="how-it-works-section">
          <h2>Как это работает</h2>
          <div className="steps-grid">
            {steps.map((step) => (
              <StepCard
                key={step.number}
                number={step.number}
                title={step.title}
                description={step.description}
              >
                <div className="step-icon-box" aria-hidden>{step.icon}</div>
              </StepCard>
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
          description="Начни тест прямо сейчас и получи персональные рекомендации."
          action={
            <Link href={testEntryHref} className="header-btn header-btn-primary">
              Начать тест бесплатно →
            </Link>
          }
        />
      </main>

      <SiteFooter />
    </div>
  );
}