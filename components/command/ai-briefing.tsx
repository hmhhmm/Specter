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
          setText(data.ai_briefing || "System stable. No critical issues detected.");
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
    <div className="w-full bg-zinc-900/40 border-b border-amber-500/10 backdrop-blur-md px-8 py-3 flex items-center gap-4 overflow-hidden">
      <div className="flex items-center gap-2 shrink-0">
        <div className="relative">
          <Brain className="w-4 h-4 text-amber-500" />
          <motion.div 
            animate={{ opacity: [0.2, 1, 0.2] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="absolute inset-0 bg-amber-500 blur-sm rounded-full -z-10"
          />
        </div>
        <span className="text-[10px] font-mono text-amber-500/60 uppercase tracking-widest font-bold">
          AI Briefing
        </span>
      </div>
      
      <div className="h-4 w-px bg-white/5" />
      
      <div className="font-mono text-[11px] text-zinc-400 tracking-tight">
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
