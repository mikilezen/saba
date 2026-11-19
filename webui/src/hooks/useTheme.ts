import {
  createContext,
  createElement,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

type Theme = "light" | "dark";
const STORAGE_KEY = "saba-webui.theme.v2";
const ThemeContext = createContext<Theme>("light");

function readStoredTheme(): Theme {
  try {
    return localStorage.getItem(STORAGE_KEY) === "light" ? "light" : "dark";
  } catch {
    return "dark";
  }
}

function applyTheme(theme: Theme): void {
  const root = document.documentElement;
  if (theme === "dark") root.classList.add("dark");
  else root.classList.remove("dark");

  const themeColor = document.querySelector<HTMLMetaElement>('meta[name="theme-color"]');
  const color =
    theme === "dark"
      ? themeColor?.dataset.themeColorDark
      : themeColor?.dataset.themeColorLight;
  if (themeColor && color) themeColor.content = color;
}

export function useTheme(): {
  theme: Theme;
  toggle: () => void;
  setTheme: (t: Theme) => void;
} {
  const [theme, setThemeState] = useState<Theme>(readStoredTheme);

  useEffect(() => {
    applyTheme(theme);
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch {
      // ignore
    }
  }, [theme]);

  const setTheme = useCallback((nextTheme: Theme) => setThemeState(nextTheme), []);
  const toggle = useCallback(() => {
    setThemeState((current) => current === "dark" ? "light" : "dark");
  }, []);
  return { theme, toggle, setTheme };
}

export function ThemeProvider({ theme, children }: { theme: Theme; children: ReactNode }) {
  return createElement(ThemeContext.Provider, { value: theme }, children);
}

export function useThemeValue(): Theme {
  return useContext(ThemeContext);
}
