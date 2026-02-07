"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Cpu } from "lucide-react";
import { useState } from "react";

interface EvidencePreviewProps {
  cloudPosition: { x: number; y: number };
}

export function EvidencePreview({ cloudPosition }: EvidencePreviewProps) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div 
      className="relative aspect-video bg-black rounded-xl border border-white/5 overflow-hidden group/evidence cursor-crosshair"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Mock App UI Wireframe */}
      <div className="absolute inset-0 p-4 opacity-10 pointer-events-none transition-opacity duration-700 group-hover/evidence:opacity-20">
        <div className="h-6 w-1/3 bg-white/20 rounded mb-4" />
        <div className="grid grid-cols-2 gap-4 h-full pb-12">
          <div className="bg-white/10 rounded-lg border border-white/10" />
          <div className="space-y-3">
            <div className="h-4 w-full bg-white/10 rounded" />
            <div className="h-4 w-5/6 bg-white/10 rounded" />
            <div className="h-12 w-full bg-emerald-500/20 rounded border border-emerald-500/20" />
            <div className="h-4 w-1/2 bg-white/10 rounded" />
          </div>
        </div>
      </div>

      {/* Grid Pattern Overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:10px_10px] pointer-events-none" />

      {/* Scanline Animation */}
      <motion.div 
        animate={{ 
          top: ["-10%", "110%"],
          opacity: [0.1, 0.3, 0.1]
        }}
        transition={{ 
          duration: 3, 
          repeat: Infinity, 
          ease: "linear" 
        }}
        className="absolute left-0 right-0 h-1 bg-emerald-500/30 blur-[2px] z-10"
      />

      {/* The Neural Cloud (Uncertainty Heatmap) */}
      <AnimatePresence>
        {isHovered && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ 
              opacity: 0.5, 
              scale: [1, 1.1, 1],
            }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ 
              duration: 2, 
              repeat: Infinity,
              ease: "easeInOut"
            }}
            className="absolute pointer-events-none z-20"
            style={{
              left: `${cloudPosition.x}%`,
              top: `${cloudPosition.y}%`,
              width: "150px",
              height: "150px",
              transform: "translate(-50%, -50%)",
              background: "radial-gradient(circle, rgba(239,68,68,0.4) 0%, rgba(239,68,68,0.1) 40%, transparent 70%)",
              filter: "blur(20px)",
            }}
          />
        )}
      </AnimatePresence>

      {/* Label and Status */}
      <div className="absolute bottom-3 left-3 flex items-center gap-2 z-30">
        <div className="p-1 rounded bg-black/60 border border-white/10 backdrop-blur-md">
          <Cpu className="w-3 h-3 text-emerald-500" />
        </div>
        <span className="text-[8px] font-mono text-zinc-400 uppercase tracking-[0.2em]">Ghost Replay v1.58</span>
      </div>

      <div className="absolute top-3 right-3 z-30">
        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-red-500/10 border border-red-500/20">
          <div className="w-1 h-1 rounded-full bg-red-500 animate-pulse" />
          <span className="text-[8px] font-mono text-red-500 uppercase tracking-widest">Heatmap Active</span>
        </div>
      </div>

      {/* Atmospheric Flickering */}
      <motion.div 
        animate={{ opacity: [0.02, 0.05, 0.02] }}
        transition={{ duration: 0.1, repeat: Infinity }}
        className="absolute inset-0 bg-white pointer-events-none mix-blend-overlay z-0"
      />
    </div>
  );
}
