"use client";

import { motion, AnimatePresence } from "framer-motion";
import { IncidentCard, Incident } from "./incident-card";

const MOCK_INCIDENTS: Incident[] = [
  {
    id: "0844",
    severity: "P0",
    title: "Mobile Z-Index Collision",
    type: "z-index",
    device: "iPhone 15 Pro",
    confidence: 98,
    revenueLoss: 12400,
    cloudPosition: { x: 80, y: 88 },
    monologue: "Critical vision analysis confirmed. Chat widget (z-9999) is physically overlapping the 'Sell' execution button on mobile viewport. User intent is physically blocked. Business impact: 100% bounce rate for mobile trade intents.",
    remediation: "Set z-index of primary execution buttons to > 10001. Restrict support widget height on mobile viewports to prevent obstruction of interactive components.",
  },
  {
    id: "0843",
    severity: "P0",
    title: "Price Field Data Overflow",
    type: "overflow",
    device: "Samsung S23",
    confidence: 94,
    revenueLoss: 8900,
    cloudPosition: { x: 40, y: 28 },
    monologue: "Visual integrity failure detected. BTC Price field exceeds container bounds and clips at viewport edge. 40% of the numerical string is unreadable, causing high user uncertainty and trade abandonment.",
    remediation: "Remove fixed-width containers from dynamic price displays. Implement 'overflow-wrap: anywhere' or responsive font sizing using 'clamp()' to ensure full visibility.",
  },
  {
    id: "0842",
    severity: "P1",
    title: "Contrast Ratio Violation",
    type: "contrast",
    device: "Desktop Chrome",
    confidence: 88,
    revenueLoss: 4200,
    cloudPosition: { x: 70, y: 62 },
    monologue: "Accessibility audit failed. 'Transaction Fee' value is hardcoded to black on a dark background. Functionally invisible to the human eye. Contrast ratio: 1.1:1. High risk of hidden-fee customer complaints.",
    remediation: "Replace hardcoded hex #000000 with semantic Tailwind classes (e.g., 'text-zinc-400') to ensure WCAG 2.1 AA compliance across light and dark modes.",
  },
  {
    id: "0841",
    severity: "P2",
    title: "Keyboard Mismatch Friction",
    type: "keyboard",
    device: "iPhone 15 Pro",
    confidence: 82,
    revenueLoss: 1800,
    cloudPosition: { x: 70, y: 52 },
    monologue: "UX friction detected. 'Amount' input triggers standard alpha keyboard (ABC) instead of numeric pad. Observed user 'rage-clicking' and manual keyboard switching. Significant drag on micro-conversion speed.",
    remediation: "Explicitly set 'inputmode=decimal' and 'type=text' with a numeric pattern. This forces the native OS to surface the numeric keypad immediately.",
  },
  {
    id: "0840",
    severity: "P1",
    title: "Localization Container Break",
    type: "i18n",
    device: "Desktop Chrome (DE)",
    confidence: 91,
    revenueLoss: 3100,
    cloudPosition: { x: 70, y: 68 },
    monologue: "I18n breakage detected. German string 'Handel bestätigen' overflows the fixed-width 180px button. Visual clipped text reduces brand trust and execution confidence for European users.",
    remediation: "Transition from fixed 'w-[180px]' to 'min-w-[180px]' with 'w-auto' and horizontal padding. Allow containers to scale based on translated string length.",
  },
  {
    id: "0839",
    severity: "P2",
    title: "Silent Functional Failure",
    type: "phantom",
    device: "Samsung S23",
    confidence: 76,
    revenueLoss: 4500,
    cloudPosition: { x: 70, y: 78 },
    monologue: "Phantom failure confirmed. 'Withdraw' button registers a click but triggers zero UI feedback. No state change, no toast, no spinner. User remains in an unconfirmed state with no indication of success.",
    remediation: "Implement a global feedback hook. Every user interaction must trigger a visual state change (spinner, toast, or disabled state) until the backend promise resolves.",
  },
  {
    id: "0838",
    severity: "P0",
    title: "Infinite Loading Dead-End",
    type: "dead-end",
    device: "iPhone 15 Pro",
    confidence: 99,
    revenueLoss: 15600,
    cloudPosition: { x: 50, y: 50 },
    monologue: "Total session termination detected. Global overlay active for > 15 seconds. DOM is locked and all pointer events are blocked. No exit path for user. Complete conversion loss.",
    remediation: "Implement a 10-second watchdog timer on global spinners. If timeout occurs, force-clear the overlay and surface a 'Retry Connection' button.",
  },
];

interface IncidentGridProps {
  activeFilter: string;
}

export function IncidentGrid({ activeFilter }: IncidentGridProps) {
  const filteredIncidents = activeFilter === "all" 
    ? MOCK_INCIDENTS 
    : MOCK_INCIDENTS.filter(i => i.severity === activeFilter);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 auto-rows-fr">
      <AnimatePresence mode="popLayout">
        {filteredIncidents.map((incident, index) => (
          <motion.div
            key={incident.id}
            layout
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.4, delay: index * 0.05 }}
          >
            <IncidentCard incident={incident} index={index} />
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
