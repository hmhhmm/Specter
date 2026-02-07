"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";
import { IncidentCard, Incident } from "./incident-card";

const FALLBACK_INCIDENTS: Incident[] = [
  {
    id: "0412",
    severity: "P0",
    title: "Hidden Checkout Button on Mobile Viewport",
    device: "Android Pixel 7",
    confidence: 98,
    revenueLoss: 12400,
    cloudPosition: { x: 65, y: 35 },
    monologue: "Critical friction detected at terminal stage. The 'Complete Purchase' element is completely obscured by a persistent cookie banner.",
  },
  {
    id: "0411",
    severity: "P1",
    title: "Vague Error Message on OTP Verification",
    device: "iPhone 15 Pro",
    confidence: 84,
    revenueLoss: 4200,
    cloudPosition: { x: 30, y: 70 },
    monologue: "User entered correct OTP but received a generic 'Something went wrong' alert.",
  },
];

interface IncidentGridProps {
  activeFilter: string;
}

export function IncidentGrid({ activeFilter }: IncidentGridProps) {
  const [incidents, setIncidents] = useState<Incident[]>(FALLBACK_INCIDENTS);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchIncidents() {
      try {
        setLoading(true);
        const response = await fetch("http://localhost:8000/api/incidents?limit=50");
        if (!response.ok) throw new Error("Failed to fetch incidents");
        
        const data = await response.json();
        
        if (data.incidents && data.incidents.length > 0) {
          // Transform API data to match Incident interface
          const transformedIncidents: Incident[] = data.incidents.map((incident: any, index: number) => ({
            id: incident.id || `inc-${index}`,
            severity: incident.severity || "P2",
            title: incident.title || "Unknown Issue",
            device: incident.device || "Unknown Device",
            confidence: incident.confidence || 75,
            revenueLoss: incident.revenueLoss || 1000,
            cloudPosition: incident.cloudPosition || { x: 50, y: 50 },
            monologue: incident.monologue || "Analysis in progress...",
          }));
          setIncidents(transformedIncidents);
        }
        setError(null);
      } catch (err: any) {
        console.error("Error fetching incidents:", err);
        setError(err.message);
        // Keep fallback data on error
      } finally {
        setLoading(false);
      }
    }

    fetchIncidents();
  }, []);

  const filteredIncidents = activeFilter === "all" 
    ? incidents 
    : incidents.filter(i => i.severity === activeFilter);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-[500px] rounded-[2rem] bg-zinc-900/40 border border-white/5 animate-pulse" />
        ))}
      </div>
    );
  }

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
      {filteredIncidents.length === 0 && (
        <div className="col-span-full text-center py-20 text-zinc-600 font-mono text-sm">
          No incidents found for filter: {activeFilter}
        </div>
      )}
    </div>
  );
}
