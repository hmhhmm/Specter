# Specter.AI - Mock Engine Specs (Target Dashboard)

## Overview
The Mock Engine (`/mock-target`) is a deterministic "Testing Playground" designed to simulate high-impact UI/UX failures that are undetectable by traditional logging or unit tests. It serves as the target for the **Ghost AI** agent.

## Architecture: The Glass Layer
To maintain a clean separation between the "Agent" and the "Target," we use a **Glass Layer Architecture**:
1. **Target Site (`/mock-target`):** A standard Next.js page loaded inside an `iframe`.
2. **Glass Layer (`DeviceEmulator`):** A transparent, `pointer-events-none` `div` positioned absolutely over the iframe.
3. **Ghost AI Overlay:** All AI annotations, the `GhostCursor`, and scanlines exist ONLY in the Glass Layer. This prevents the AI's presence from polluting the target's DOM.

## Inter-Frame Communication
The parent simulation (`/lab`) communicates with the target iframe using `window.postMessage`. This is used to trigger state changes that mimic user behavior:
- `SET_LANG`: Switches between 'en' and 'de' to test localization.
- `SHOW_SPINNER`: Triggers a global loading state to test "Dead-End" detection.

---

## The 7 "Financial Anxiety" Bugs (QA Traps)

### 1. The Z-Index Trap (Mobile Exclusive)
- **Technical Implementation:** A floating Chat Bubble (`z-[9999]`) is positioned at `bottom-6 right-6`.
- **The Bug:** On narrow viewports, it partially overlaps the "Sell" button.
- **Why it's a Trap:** Traditional Selenium/Playwright tests might report the button as "clickable," but a human (or AI) can see the obstruction.

### 2. Data Overflow (Layout Shift)
- **Technical Implementation:** BTC Price text uses `text-7xl` with `whitespace-nowrap`.
- **The Bug:** When the price hits 5+ digits, it overflows the container width and clips at the viewport edge.
- **Why it's a Trap:** Tests for "Text Presence" will pass, but "Visual Integrity" fails.

### 3. The Invisible Fee (Contrast Failure)
- **Technical Implementation:** The Fee Value is hardcoded to `color: #0a0a0c` (identical to the background).
- **The Bug:** The label "Transaction Fee:" is visible, but the amount is invisible.
- **Why it's a Trap:** The element exists in the DOM, but it has a 1:1 contrast ratio.

### 4. The Rage Input (UX Friction)
- **Technical Implementation:** The Amount input uses `type="text"` instead of `inputmode="numeric"`.
- **The Bug:** Triggers the Alpha keyboard (ABC) on mobile instead of the Number Pad (123).
- **Why it's a Trap:** It doesn't "break" the site, but it causes significant user frustration and churn.

### 5. Localization Break (Fixed-Width Overflow)
- **Technical Implementation:** The Trade button has a fixed `w-[180px]`.
- **The Bug:** German translation "Handel bestätigen" is longer than the English "Confirm Trade," causing it to overflow the button boundary.
- **Why it's a Trap:** Highlight's the danger of fixed-width containers in i18n.

### 6. The Phantom Error (Silent Functional Fail)
- **Technical Implementation:** The "Withdraw" button executes a function that simply logs to the console with no UI feedback or state change.
- **The Bug:** User clicks, but nothing happens. No error message, no success message.
- **Why it's a Trap:** Tests for "Function Called" pass, but the "User Feedback Loop" is broken.

### 7. The Dead-End Spinner (Global State Lock)
- **Technical Implementation:** A full-screen overlay with a `z-index: 10000` and an infinite spinner.
- **The Bug:** All `pointer-events` are blocked. The user is stuck indefinitely.
- **Why it's a Trap:** Simulates a crashed backend process or unhandled promise that locks the UI.

---

## Technical Goal for Ghost AI
The backend implementation must utilize **Vision-based Analysis** (e.g., GPT-4o-vision or Claude 3.5 Sonnet) to detect these issues by "looking" at the rendered pixels, as DOM-only analysis will miss most of these "Anxiety" bugs.
