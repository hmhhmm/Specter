export interface HealerScenario {
  bugId: string;
  bugTitle: string;
  bugDescription: string;
  severity: "P0" | "P1" | "P2" | "P3";
  filePath: string;
  fixHint: string;
}

export const HEALER_SCENARIOS: HealerScenario[] = [
  {
    bugId: "contrast-1",
    bugTitle: "Invisible Fee Visibility",
    bugDescription: "Transaction fee value is invisible due to black-on-black contrast (color: #0a0a0c on background #0a0a0c).",
    severity: "P1",
    filePath: "app/mock-target/page.tsx",
    fixHint: "Change the inline style 'color: #0a0a0c' to a high-contrast color like zinc-100 or emerald-500. Use Tailwind classes if possible or a hex code like #f4f4f5.",
  },
  {
    bugId: "z-index-1",
    bugTitle: "Z-Index Overlay Obstruction",
    bugDescription: "Chat bubble with z-[9999] overlaps primary action buttons on mobile viewports, making them unclickable.",
    severity: "P0",
    filePath: "app/mock-target/page.tsx",
    fixHint: "Reduce the z-index from z-[9999] to something lower like z-40, or move the bubble to avoid overlapping critical buttons like 'Sell'.",
  },
  {
    bugId: "layout-1",
    bugTitle: "Button Label Overflow",
    bugDescription: "Confirm Trade button has a fixed width (w-[180px]) which causes German text 'Handel bestätigen' to overflow or look cramped.",
    severity: "P2",
    filePath: "app/mock-target/page.tsx",
    fixHint: "Replace the fixed width 'w-[180px]' with 'w-full' or 'min-w-[180px]' and 'w-auto' to allow for internationalization flexibility.",
  },
  {
    bugId: "input-1",
    bugTitle: "Mobile Keyboard Type Mismatch",
    bugDescription: "Amount input uses type='text' instead of numeric inputmode, causing the full alphanumeric keyboard to appear on mobile.",
    severity: "P2",
    filePath: "app/mock-target/page.tsx",
    fixHint: "Change 'type=\"text\"' to 'type=\"number\"' and add 'inputMode=\"decimal\"' for the best mobile numeric keyboard experience.",
  }
];
