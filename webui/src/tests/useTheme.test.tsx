import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { useTheme } from "@/hooks/useTheme";

describe("useTheme", () => {
  beforeEach(() => {
    localStorage.removeItem("saba-webui.theme.v2");
    document.documentElement.classList.remove("dark");

    const themeColor = document.createElement("meta");
    themeColor.name = "theme-color";
    themeColor.content = "#ffffff";
    themeColor.dataset.themeColorLight = "#ffffff";
    themeColor.dataset.themeColorDark = "#303030";
    document.head.append(themeColor);
  });

  afterEach(() => {
    document.querySelector('meta[name="theme-color"]')?.remove();
    document.documentElement.classList.remove("dark");
    localStorage.removeItem("saba-webui.theme.v2");
  });

  it("restores and toggles the saved theme", () => {
    localStorage.setItem("saba-webui.theme.v2", "dark");
    const { result } = renderHook(useTheme);
    const themeColor = document.querySelector<HTMLMetaElement>('meta[name="theme-color"]');

    expect(document.documentElement).toHaveClass("dark");
    expect(themeColor?.content).toBe("#303030");
    expect(localStorage.getItem("saba-webui.theme.v2")).toBe("dark");

    act(() => result.current.toggle());
    expect(document.documentElement).not.toHaveClass("dark");
    expect(localStorage.getItem("saba-webui.theme.v2")).toBe("light");

    act(() => result.current.setTheme("dark"));
    expect(document.documentElement).toHaveClass("dark");
    expect(localStorage.getItem("saba-webui.theme.v2")).toBe("dark");
  });
});
