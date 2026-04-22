export type OnboardingProfile = {
  surname: string;
  name: string;
  patronymic?: string;
  age: number | null;
  gender: "male" | "female" | "";
  school: string;
  grade: number | null;
  phone: string;
  email: string;
  completedAt?: string | null;
};

const PROFILE_STORAGE_KEY = "onboarding_profile";
const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";
const ACCOUNT_EMAIL_KEY = "auth_email";
const PENDING_VERIFICATION_EMAIL_KEY = "pending_verification_email";
const POST_LOGIN_REDIRECT_KEY = "post_login_redirect";

function getProfileStorageKey(email?: string): string {
  const normalizedEmail = (email ?? getAccountEmail()).trim().toLowerCase();
  return normalizedEmail ? `${PROFILE_STORAGE_KEY}:${normalizedEmail}` : PROFILE_STORAGE_KEY;
}

export function isAuthenticated(): boolean {
  if (typeof window === "undefined") {
    return false;
  }
  return Boolean(localStorage.getItem(ACCESS_TOKEN_KEY));
}

export function getOnboardingProfile(): OnboardingProfile | null {
  if (typeof window === "undefined") {
    return null;
  }

  const currentEmail = getAccountEmail();
  const scopedRaw = localStorage.getItem(getProfileStorageKey(currentEmail));
  if (scopedRaw) {
    try {
      return JSON.parse(scopedRaw) as OnboardingProfile;
    } catch {
      localStorage.removeItem(getProfileStorageKey(currentEmail));
    }
  }

  const legacyRaw = localStorage.getItem(PROFILE_STORAGE_KEY);
  if (!legacyRaw) {
    return null;
  }

  try {
    const legacyProfile = JSON.parse(legacyRaw) as OnboardingProfile;
    if (
      currentEmail &&
      legacyProfile.email?.trim().toLowerCase() === currentEmail.trim().toLowerCase()
    ) {
      return legacyProfile;
    }
  } catch {
    localStorage.removeItem(PROFILE_STORAGE_KEY);
  }

  return null;
}

export function saveOnboardingProfile(profile: OnboardingProfile): void {
  if (typeof window === "undefined") {
    return;
  }
  localStorage.setItem(
    getProfileStorageKey(profile.email),
    JSON.stringify(profile)
  );
}

export function setAccountEmail(email: string): void {
  if (typeof window === "undefined") {
    return;
  }
  const normalizedEmail = email.trim().toLowerCase();
  localStorage.setItem(ACCOUNT_EMAIL_KEY, normalizedEmail);
  window.dispatchEvent(new Event("careerpath:auth-changed"));
}

export function getAccountEmail(): string {
  if (typeof window === "undefined") {
    return "";
  }
  return localStorage.getItem(ACCOUNT_EMAIL_KEY) ?? "";
}

export function setPendingVerificationEmail(email: string): void {
  if (typeof window === "undefined") {
    return;
  }
  localStorage.setItem(PENDING_VERIFICATION_EMAIL_KEY, email.trim().toLowerCase());
}

export function getPendingVerificationEmail(): string {
  if (typeof window === "undefined") {
    return "";
  }
  return localStorage.getItem(PENDING_VERIFICATION_EMAIL_KEY) ?? "";
}

export function clearPendingVerificationEmail(): void {
  if (typeof window === "undefined") {
    return;
  }
  localStorage.removeItem(PENDING_VERIFICATION_EMAIL_KEY);
}

export function clearAuthStorage(): void {
  if (typeof window === "undefined") {
    return;
  }
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(ACCOUNT_EMAIL_KEY);
  localStorage.removeItem(PROFILE_STORAGE_KEY);
  localStorage.removeItem(PENDING_VERIFICATION_EMAIL_KEY);
  window.dispatchEvent(new Event("careerpath:auth-changed"));
}

function normalizeRedirectPath(path: string): string {
  if (!path.startsWith("/")) return "/dashboard";
  if (path.startsWith("/test")) return "/";
  if (path.startsWith("/login") || path.startsWith("/register")) return "/dashboard";
  return path;
}

export function rememberPostLoginRedirect(path: string): void {
  if (typeof window === "undefined") {
    return;
  }
  localStorage.setItem(POST_LOGIN_REDIRECT_KEY, normalizeRedirectPath(path));
}

export function consumePostLoginRedirect(): string {
  if (typeof window === "undefined") {
    return "/dashboard";
  }
  const value = localStorage.getItem(POST_LOGIN_REDIRECT_KEY);
  localStorage.removeItem(POST_LOGIN_REDIRECT_KEY);
  if (!value) {
    return "/dashboard";
  }
  return normalizeRedirectPath(value);
}

export function isProfileComplete(profile: OnboardingProfile | null): boolean {
  if (!profile) {
    return false;
  }
  const validAge = typeof profile.age === "number" && profile.age > 0;
  const validGrade = typeof profile.grade === "number" && profile.grade > 0;
  const accountEmail = getAccountEmail();
  const effectiveEmail = accountEmail || profile.email;

  return Boolean(
    profile.surname?.trim() &&
      profile.name?.trim() &&
      validAge &&
      (profile.gender === "male" || profile.gender === "female") &&
      profile.school?.trim() &&
      validGrade &&
      profile.phone?.trim() &&
      effectiveEmail?.trim()
  );
}

export function getTestEntryRoute(): "/login" | "/onboarding" | "/test" {
  if (!isAuthenticated()) {
    return "/login";
  }
  return isProfileComplete(getOnboardingProfile()) ? "/test" : "/onboarding";
}
