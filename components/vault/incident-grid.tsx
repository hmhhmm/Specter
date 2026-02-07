"use client";

import { motion, AnimatePresence } from "framer-motion";
import { IncidentCard, Incident } from "./incident-card";

const MOCK_INCIDENTS: Incident[] = [
  {
    id: "0412",
    severity: "P0",
    title: "Hidden Checkout Button on Mobile Viewport",
    device: "Android Pixel 7",
    confidence: 98,
    revenueLoss: 12400,
    cloudPosition: { x: 65, y: 35 },
    monologue: "Critical friction detected at terminal stage. The 'Complete Purchase' element is completely obscured by a persistent cookie banner. Frustration levels peaking as user attempts to scroll but triggers inadvertent clicks on irrelevant links. Business impact: 100% bounce rate for Pixel 7 users in the last 4 hours.",
  },
  {
    id: "0411",
    severity: "P1",
    title: "Vague Error Message on OTP Verification",
    device: "iPhone 15 Pro",
    confidence: 84,
    revenueLoss: 4200,
    cloudPosition: { x: 30, y: 70 },
    monologue: "User entered correct OTP but received a generic 'Something went wrong' alert. System logs show a timeout on the verification microservice, but the UI fails to explain or offer a retry. User is confused, repeatedly tapping the submit button which triggers a rate limit. Visual uncertainty: The error message is nearly the same color as the background.",
  },
  {
    id: "0410",
    severity: "P2",
    title: "Layout Shift During Image Lazy Loading",
    device: "iPad Pro",
    confidence: 76,
    revenueLoss: 1800,
    cloudPosition: { x: 50, y: 50 },
    monologue: "Observed significant CLS (Cumulative Layout Shift) when product images hydrate. User was about to tap 'Add to Cart' when a high-res image loaded, shifting the page down and causing the user to click a 'Sign out' button instead. This is a classic 'silent killer' of conversion that metrics don't capture as an error.",
  },
  {
    id: "0409",
    severity: "P0",
    title: "Silent Failure on Social OAuth Login",
    device: "Samsung S24 Ultra",
    confidence: 92,
    revenueLoss: 8900,
    cloudPosition: { x: 20, y: 20 },
    monologue: "Google Login flow hangs indefinitely after account selection. The UI remains in a 'thinking' state with no timeout or fallback. Visual scan shows the spinner is misaligned, overlapping the header. Users on S24 Ultra are effectively locked out of the core application loop. Priority 0 escalation required.",
  },
  {
    id: "0408",
    severity: "P3",
    title: "Misaligned Icon in Global Navigation",
    device: "Desktop Chrome",
    confidence: 65,
    revenueLoss: 450,
    cloudPosition: { x: 80, y: 15 },
    monologue: "Minor visual misalignment in the 'Settings' gear icon. It sits 4px higher than neighboring elements. While low impact, it signals a lack of polish to premium users. AI confidence lower here as it's purely aesthetic, but the inconsistency is noted across 3 different screen sizes.",
  },
  {
    id: "0407",
    severity: "P1",
    title: "Infinite Spinner on Profile Update",
    device: "Pixel Fold",
    confidence: 81,
    revenueLoss: 3100,
    cloudPosition: { x: 45, y: 60 },
    monologue: "Form submission for user profile updates is returning a 204 but the UI never transitions out of the loading state. User is left waiting for a confirmation that already happened on the server. Most users refresh the page, which clears their unsaved changes. High frustration due to wasted effort.",
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
