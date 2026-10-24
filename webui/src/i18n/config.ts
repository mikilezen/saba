export const LOCALE_STORAGE_KEY = "saba.locale";

export const supportedLocales = [
  { code: "en", nativeLabel: "English" },
  { code: "am", nativeLabel: "አማርኛ" },
  { code: "om", nativeLabel: "Afaan Oromoo" },
  { code: "ti", nativeLabel: "ትግርኛ" },
] as const;

export type SupportedLocale = (typeof supportedLocales)[number]["code"];

export const defaultLocale: SupportedLocale = "en";
export const fallbackLocale: SupportedLocale = "en";

export function normalizeLocale(
  input: string | null | undefined,
): SupportedLocale {
  if (!input) return defaultLocale;
  const trimmed = input.trim();
  if (!trimmed) return defaultLocale;

  const exact = supportedLocales.find((locale) => locale.code === trimmed);
  if (exact) return exact.code;

  const lower = trimmed.toLowerCase();
  const aliases: Record<string, SupportedLocale> = {
    amh: "am",
    amharic: "am",
    oro: "om",
    oromo: "om",
    tgr: "ti",
    tigrinya: "ti",
  };
  if (aliases[lower]) return aliases[lower];

  const base = lower.split("-")[0];
  const baseMatch = supportedLocales.find(
    (locale) => locale.code.toLowerCase() === base,
  );
  return baseMatch?.code ?? defaultLocale;
}

function readStoredLocale(): SupportedLocale | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(LOCALE_STORAGE_KEY);
    return raw ? normalizeLocale(raw) : null;
  } catch {
    return null;
  }
}

export function resolveInitialLocale(): SupportedLocale {
  return readStoredLocale() ?? defaultLocale;
}

export function persistLocale(locale: SupportedLocale): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(LOCALE_STORAGE_KEY, locale);
  } catch {
    // ignore storage errors
  }
}

export function applyDocumentLocale(locale: SupportedLocale): void {
  if (typeof document === "undefined") return;
  document.documentElement.lang = locale;
}
