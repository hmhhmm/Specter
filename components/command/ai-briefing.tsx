"use client";

import { motion } from "framer-motion";
import { Brain } from "lucide-react";
import { useEffect, useState } from "react";

export function AIBriefing() {
  const [text, setText] = useState("Initializing Specter AI analysis...");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchBriefing() {
      try {
        const response = await fetch("http://localhost:8000/api/dashboard/stats");
        if (response.ok) {
          const data = await response.json();
          setText(data.ai_briefing || "Stable. No critical issues detected.");
        }
      } catch (err) {
        setText("Backend connection pending. Run tests to populate dashboard.");
      } finally {
        setLoading(false);
      }
    }
    fetchBriefing();
  }, []);
  
  return (
    <div className="w-full bg-zinc-100/60 dark:bg-zinc-900/60 border-b border-zinc-200 dark:border-zinc-800 backdrop-blur-sm px-8 py-3 flex items-center gap-4 overflow-hidden transition-colors duration-300">
      <div className="font-mono text-[11px] text-zinc-600 dark:text-zinc-400 tracking-tight transition-colors duration-300">
        <motion.span
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          {text.split("").map((char, i) => (
            <motion.span
              key={i}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.05, delay: i * 0.02 + 0.5 }}
            >
              {char}
            </motion.span>
          ))}
          <motion.span
            animate={{ opacity: [1, 0] }}
            transition={{ duration: 0.8, repeat: Infinity, ease: [1, 1, 0, 0] }}
            className="inline-block w-1.5 h-3 bg-amber-500 ml-1 align-middle"
          />
        </motion.span>
      </div>
    </div>
  );
}
