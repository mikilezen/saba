import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { useTheme } from "@/hooks/useTheme";

describe("useTheme", () => {
  beforeEach(() => {
    localStorage.removeItem("saba-webui.theme");
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
    localStorage.removeItem("saba-webui.theme");
  });

  it("always uses the light theme", () => {
    localStorage.setItem("saba-webui.theme", "dark");
    const { result } = renderHook(useTheme);
    const themeColor = document.querySelector<HTMLMetaElement>('meta[name="theme-color"]');

    expect(document.documentElement).not.toHaveClass("dark");
    expect(themeColor?.content).toBe("#ffffff");
    expect(localStorage.getItem("saba-webui.theme")).toBe("light");

    act(() => result.current.setTheme("dark"));
    expect(document.documentElement).not.toHaveClass("dark");
    expect(localStorage.getItem("saba-webui.theme")).toBe("light");
  });
});
