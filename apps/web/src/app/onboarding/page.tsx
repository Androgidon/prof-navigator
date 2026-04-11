"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { SiteHeader } from "@/components/layout/site-header";
import { SiteFooter } from "@/components/layout/site-footer";
import { FocusedTaskLayout } from "@/components/layout/focused-task-layout";
import { ProgressBar } from "@/components/layout/progress-bar";
import {
  getAccountEmail,
  getOnboardingProfile,
  isProfileComplete,
  saveOnboardingProfile,
  type OnboardingProfile,
} from "@/lib/auth-flow";

type FieldErrors = Partial<
  Record<
    "surname" | "name" | "age" | "gender" | "school" | "grade" | "phone" | "email",
    string
  >
>;

const REQUIRED_MESSAGE = "Это поле обязательно для заполнения";

const formatUzPhone = (value: string): string => {
  const onlyDigits = value.replace(/\D/g, "");
  const localDigits = onlyDigits.startsWith("998") ? onlyDigits.slice(3) : onlyDigits;
  const digits = localDigits.slice(0, 9);

  if (!digits) {
    return "+998";
  }

  const p1 = digits.slice(0, 2);
  const p2 = digits.slice(2, 5);
  const p3 = digits.slice(5, 7);
  const p4 = digits.slice(7, 9);

  let formatted = "+998";
  if (p1) formatted += ` ${p1}`;
  if (p2) formatted += ` ${p2}`;
  if (p3) formatted += ` ${p3}`;
  if (p4) formatted += ` ${p4}`;

  return formatted;
};

const createEmptyProfile = (): OnboardingProfile => ({
  surname: "",
  name: "",
  patronymic: "",
  age: null,
  gender: "",
  school: "",
  grade: null,
  phone: "",
  email: getAccountEmail(),
  completedAt: null,
});

const validateProfile = (profile: OnboardingProfile): FieldErrors => {
  const errors: FieldErrors = {};

  if (!profile.surname.trim()) errors.surname = REQUIRED_MESSAGE;
  if (!profile.name.trim()) errors.name = REQUIRED_MESSAGE;
  if (!profile.school.trim()) errors.school = REQUIRED_MESSAGE;
  if (!profile.email.trim()) errors.email = REQUIRED_MESSAGE;

  if (profile.age === null || profile.age <= 0) {
    errors.age = "Введите корректный возраст";
  }

  if (!profile.gender) {
    errors.gender = "Выберите пол";
  }

  if (profile.grade === null || profile.grade <= 0) {
    errors.grade = REQUIRED_MESSAGE;
  }

  if (!profile.phone.trim()) {
    errors.phone = REQUIRED_MESSAGE;
  } else if (!/^\+998\s\d{2}\s\d{3}\s\d{2}\s\d{2}$/.test(profile.phone)) {
    errors.phone = "Введите контактный номер телефона";
  }

  return errors;
};

export default function OnboardingPage() {
  const router = useRouter();
  const initialProfile = (() => {
    const stored = getOnboardingProfile();
    if (stored) {
      return {
        ...stored,
        phone: stored.phone ? formatUzPhone(stored.phone) : "",
        email: getAccountEmail() || stored.email,
      };
    }
    return createEmptyProfile();
  })();

  const [profile, setProfile] = useState<OnboardingProfile>(initialProfile);
  const [isSaved, setIsSaved] = useState<boolean>(
    Boolean(initialProfile.completedAt) && isProfileComplete(initialProfile)
  );
  const [isEditing, setIsEditing] = useState<boolean>(
    !(Boolean(initialProfile.completedAt) && isProfileComplete(initialProfile))
  );
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});

  const setField = <K extends keyof OnboardingProfile>(key: K, value: OnboardingProfile[K]) => {
    setProfile((prev) => ({ ...prev, [key]: value }));
    setIsSaved(false);
    setFieldErrors((prev) => ({ ...prev, [key]: undefined }));
  };

  const handleSave = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const errors = validateProfile(profile);
    setFieldErrors(errors);

    if (Object.values(errors).some(Boolean)) {
      setIsSaved(false);
      return;
    }

    const completedProfile = { ...profile, completedAt: new Date().toISOString() };
    saveOnboardingProfile(completedProfile);
    setProfile(completedProfile);
    setIsSaved(isProfileComplete(completedProfile));
    setIsEditing(false);
  };

  const canGoToTest = isSaved && isProfileComplete(profile);

  const handleGoToTest = () => {
    if (!canGoToTest) {
      return;
    }
    router.push("/test");
  };

  return (
    <div className="min-h-screen bg-background">
      <SiteHeader />
      <FocusedTaskLayout>
        <ProgressBar value={20} max={100} />
        <div className="w-full max-w-5xl mx-auto">
          <div className="auth-form-surface w-full px-6 py-6 md:px-10 md:py-8" style={{ maxWidth: "none" }}>
            <p className="text-xs font-semibold uppercase tracking-widest text-primary mb-3">
              Профиль
            </p>
            <h1>Заполните профиль перед тестом</h1>
            <p>Нужны обязательные данные, чтобы открыть прохождение теста.</p>

            <form onSubmit={handleSave}>
              <div className="space-y-5 mb-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-5">
                  <div className="form-group" style={{ marginTop: 0 }}>
                    <label htmlFor="surname" className="form-label">Фамилия *</label>
                    <input
                      id="surname"
                      name="surname"
                      required
                      className={`form-input ${fieldErrors.surname ? "border-destructive" : ""}`}
                      placeholder="Введите свою фамилию"
                      value={profile.surname}
                      readOnly={!isEditing}
                      onChange={(e) => setField("surname", e.target.value)}
                    />
                    {fieldErrors.surname && <p className="text-xs text-destructive">{fieldErrors.surname}</p>}
                  </div>

                  <div className="form-group" style={{ marginTop: 0 }}>
                    <label htmlFor="name" className="form-label">Имя *</label>
                    <input
                      id="name"
                      name="name"
                      required
                      className={`form-input ${fieldErrors.name ? "border-destructive" : ""}`}
                      placeholder="Введите своё имя"
                      value={profile.name}
                      readOnly={!isEditing}
                      onChange={(e) => setField("name", e.target.value)}
                    />
                    {fieldErrors.name && <p className="text-xs text-destructive">{fieldErrors.name}</p>}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-5">
                  <div className="form-group" style={{ marginTop: 0 }}>
                    <label htmlFor="patronymic" className="form-label">Отчество</label>
                    <input
                      id="patronymic"
                      name="patronymic"
                      className="form-input"
                      placeholder="Введите своё отчество"
                      value={profile.patronymic ?? ""}
                      readOnly={!isEditing}
                      onChange={(e) => setField("patronymic", e.target.value)}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-5">
                  <div className="form-group" style={{ marginTop: 0 }}>
                    <label htmlFor="age" className="form-label">Возраст *</label>
                    <input
                      id="age"
                      name="age"
                      type="number"
                      min={10}
                      max={99}
                      required
                      className={`form-input ${fieldErrors.age ? "border-destructive" : ""}`}
                      placeholder="Введите свой возраст"
                      value={profile.age ?? ""}
                      readOnly={!isEditing}
                      onChange={(e) => setField("age", e.target.value ? Number(e.target.value) : null)}
                    />
                    {fieldErrors.age && <p className="text-xs text-destructive">{fieldErrors.age}</p>}
                  </div>

                  <div className="form-group" style={{ marginTop: 0 }}>
                    <label htmlFor="gender" className="form-label">Пол *</label>
                    <select
                      id="gender"
                      name="gender"
                      required
                      className={`form-input ${fieldErrors.gender ? "border-destructive" : ""}`}
                      value={profile.gender}
                      disabled={!isEditing}
                      onChange={(e) => setField("gender", e.target.value as OnboardingProfile["gender"])}
                    >
                      <option value="">Выберите пол</option>
                      <option value="male">Муж</option>
                      <option value="female">Жен</option>
                    </select>
                    {fieldErrors.gender && <p className="text-xs text-destructive">{fieldErrors.gender}</p>}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-5">
                  <div className="form-group" style={{ marginTop: 0 }}>
                    <label htmlFor="school" className="form-label">Школа *</label>
                    <input
                      id="school"
                      name="school"
                      required
                      className={`form-input ${fieldErrors.school ? "border-destructive" : ""}`}
                      placeholder="Введите свою школу"
                      value={profile.school}
                      readOnly={!isEditing}
                      onChange={(e) => setField("school", e.target.value)}
                    />
                    {fieldErrors.school && <p className="text-xs text-destructive">{fieldErrors.school}</p>}
                  </div>

                  <div className="form-group" style={{ marginTop: 0 }}>
                    <label htmlFor="grade" className="form-label">Класс *</label>
                    <input
                      id="grade"
                      name="grade"
                      type="number"
                      min={1}
                      max={11}
                      required
                      className={`form-input ${fieldErrors.grade ? "border-destructive" : ""}`}
                      placeholder="Введите свой класс"
                      value={profile.grade ?? ""}
                      readOnly={!isEditing}
                      onChange={(e) => setField("grade", e.target.value ? Number(e.target.value) : null)}
                    />
                    {fieldErrors.grade && <p className="text-xs text-destructive">{fieldErrors.grade}</p>}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-5">
                  <div className="form-group" style={{ marginTop: 0 }}>
                    <label htmlFor="phone" className="form-label">Контактный номер телефона *</label>
                    <input
                      id="phone"
                      name="phone"
                      required
                      className={`form-input ${fieldErrors.phone ? "border-destructive" : ""}`}
                      inputMode="tel"
                      maxLength={17}
                      pattern="\+998\s\d{2}\s\d{3}\s\d{2}\s\d{2}"
                      placeholder="Введите свой номер телефона"
                      value={profile.phone}
                      readOnly={!isEditing}
                      onFocus={() => {
                        if (!isEditing) {
                          return;
                        }
                        if (!profile.phone) {
                          setField("phone", "+998");
                        }
                      }}
                      onChange={(e) => setField("phone", formatUzPhone(e.target.value))}
                    />
                    {fieldErrors.phone && <p className="text-xs text-destructive">{fieldErrors.phone}</p>}
                  </div>

                  <div className="form-group" style={{ marginTop: 0 }}>
                    <label htmlFor="email" className="form-label">Email *</label>
                    <input
                      id="email"
                      name="email"
                      type="email"
                      required
                      readOnly
                      className={`form-input ${fieldErrors.email ? "border-destructive" : ""}`}
                      value={profile.email}
                    />
                    {fieldErrors.email && <p className="text-xs text-destructive">{fieldErrors.email}</p>}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {isEditing ? (
                  <button type="submit" className="form-submit-btn mt-0">
                    Сохранить
                  </button>
                ) : (
                  <button type="button" className="form-submit-btn mt-0" onClick={() => setIsEditing(true)}>
                    Редактировать
                  </button>
                )}
                <button
                  type="button"
                  className="form-submit-btn mt-0"
                  onClick={handleGoToTest}
                  disabled={!canGoToTest}
                >
                  Перейти к тесту
                </button>
              </div>
            </form>
          </div>
        </div>
      </FocusedTaskLayout>
      <SiteFooter />
    </div>
  );
}
