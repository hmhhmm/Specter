"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Cpu } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

interface EvidencePreviewProps {
  cloudPosition: { x: number; y: number };
  type: "z-index" | "overflow" | "contrast" | "keyboard" | "i18n" | "phantom" | "dead-end";
}

export function EvidencePreview({ cloudPosition, type }: EvidencePreviewProps) {
  const [isHovered, setIsHovered] = useState(false);

  const renderAnnotation = () => {
    switch (type) {
      case "z-index":
        return (
          <>
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="absolute bottom-[8%] right-[8%] w-24 h-24 border-2 border-dashed border-red-500 rounded-full animate-pulse"
            />
            <div className="absolute bottom-[18%] right-[28%] px-2 py-1 bg-red-500 text-white text-[8px] font-mono font-bold uppercase tracking-tighter rounded">
              [COLLISION_DETECTED]
            </div>
            <div className="absolute bottom-[4%] right-[4%] px-2 py-1 bg-zinc-800 border border-white/10 text-zinc-400 text-[6px] font-mono uppercase rounded">
              Z-Stack: 9999 vs 100
            </div>
          </>
        );
      case "overflow":
        return (
          <>
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="absolute top-[22%] right-0 w-[40%] h-14 border-2 border-red-500 rounded flex items-center justify-end pr-2 overflow-hidden"
            >
              <div className="w-1 h-full bg-red-500/50" />
            </motion.div>
            <div className="absolute top-[14%] right-[15%] px-2 py-1 bg-red-500 text-white text-[8px] font-mono font-bold uppercase rounded">
              [CLIPPING_DETECTED]
            </div>
            <div className="absolute top-[32%] right-[5%] px-2 py-1 bg-zinc-800 border border-white/10 text-zinc-400 text-[6px] font-mono uppercase rounded">
              Width: 420px (Container: 320px)
            </div>
          </>
        );
      case "contrast":
        return (
          <>
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="absolute bottom-[20%] right-[10%] w-20 h-8 border border-amber-500 rounded bg-amber-500/5"
            />
            <div className="absolute bottom-[30%] right-[15%] px-2 py-1 bg-amber-500 text-white text-[8px] font-mono font-bold uppercase rounded">
              [CONTRAST_FAIL: 1.1:1]
            </div>
            <div className="absolute bottom-[12%] right-[10%] px-2 py-1 bg-zinc-800 border border-white/10 text-zinc-400 text-[6px] font-mono uppercase rounded">
              Target: 4.5:1 (WCAG AA)
            </div>
          </>
        );
      case "keyboard":
        return (
          <>
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="absolute top-[28%] left-[20%] w-[60%] h-10 border-2 border-blue-500 rounded bg-blue-500/5"
            />
            <div className="absolute top-[21%] left-[25%] px-2 py-1 bg-blue-500 text-white text-[8px] font-mono font-bold uppercase rounded">
              [INPUT_MODE_MISMATCH]
            </div>
            <div className="absolute top-[38%] left-[25%] px-2 py-1 bg-zinc-800 border border-white/10 text-zinc-400 text-[6px] font-mono uppercase rounded">
              Active: ABC | Expected: 123
            </div>
          </>
        );
      case "i18n":
        return (
          <>
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="absolute top-[48%] left-[25%] w-[50%] h-12 border-2 border-red-500 rounded overflow-hidden"
            >
              <div className="absolute inset-y-0 right-0 w-4 bg-red-500/20" />
            </motion.div>
            <div className="absolute top-[41%] left-[30%] px-2 py-1 bg-red-500 text-white text-[8px] font-mono font-bold uppercase rounded">
              [STRING_OVERFLOW: DE]
            </div>
            <div className="absolute top-[58%] left-[30%] px-2 py-1 bg-zinc-800 border border-white/10 text-zinc-400 text-[6px] font-mono uppercase rounded">
              Length: 18ch (Max: 12ch)
            </div>
          </>
        );
      case "phantom":
        return (
          <>
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="absolute top-[45%] left-[30%] w-[40%] h-12 border-2 border-zinc-500 rounded bg-zinc-500/10"
            />
            <div className="absolute top-[38%] left-[35%] px-2 py-1 bg-zinc-500 text-white text-[8px] font-mono font-bold uppercase rounded">
              [SILENT_FAIL_DETECTED]
            </div>
            <div className="absolute top-[55%] left-[35%] px-2 py-1 bg-zinc-800 border border-white/10 text-zinc-400 text-[6px] font-mono uppercase rounded">
              State: IDLE (Expected: MUTATING)
            </div>
          </>
        );
      case "dead-end":
        return (
          <div className="absolute inset-0 bg-red-950/30 backdrop-blur-[1px] flex items-center justify-center">
            <div className="p-3 bg-red-600 rounded border border-red-400 text-center space-y-1">
              <div className="text-[10px] font-mono font-bold text-white uppercase">[GLOBAL_LOCK]</div>
              <div className="text-[8px] font-mono text-red-200">Session Frozen: &gt;15s</div>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div 
      className="relative aspect-video bg-black rounded-xl border border-white/5 overflow-hidden group/evidence cursor-crosshair"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Target Preview Perspective - Zoomed based on type */}
      <div className={cn(
        "absolute inset-0 p-4 opacity-20 pointer-events-none transition-all duration-700 group-hover/evidence:opacity-30",
        type === "overflow" ? "scale-[1.5] origin-top" :
        type === "z-index" ? "scale-[1.8] origin-bottom-right" :
        type === "contrast" ? "scale-[1.3] origin-center" :
        type === "keyboard" ? "scale-[1.2] origin-center" :
        type === "i18n" ? "scale-[1.4] origin-bottom" :
        "scale-100"
      )}>
        {/* Synthetic UI Structure (The Digital Twin) */}
        <div className="h-full w-full flex flex-col gap-4">
          {/* Header Mock */}
          <div className="flex justify-between items-center px-2 py-1 border-b border-white/10 mb-4">
            <div className="w-8 h-2 bg-emerald-500/20 rounded" />
            <div className="w-12 h-2 bg-white/10 rounded" />
          </div>

          {/* Dynamic Content based on Bug Type */}
          <div className="flex-1 relative">
            {type === "overflow" && (
              <div className="space-y-4">
                <div className="w-16 h-2 bg-white/5 rounded" />
                <div className="text-[40px] font-bold text-white/20 whitespace-nowrap">
                  $10,420.50
                </div>
                <div className="w-full h-24 bg-white/5 rounded-xl border border-white/5" />
              </div>
            )}

            {type === "z-index" && (
              <div className="absolute inset-0 flex flex-col justify-end items-end gap-4 p-4">
                <div className="w-32 h-10 bg-emerald-500/20 rounded-lg border border-emerald-500/30" />
                <div className="w-12 h-12 bg-emerald-500/40 rounded-full border border-emerald-500/50" />
              </div>
            )}

            {type === "contrast" && (
              <div className="flex flex-col gap-8 items-center pt-8">
                <div className="w-full h-32 bg-white/5 rounded-xl border border-white/5" />
                <div className="flex justify-between w-full px-4">
                  <div className="w-20 h-2 bg-white/10 rounded" />
                  <div className="w-12 h-2 bg-zinc-900 rounded" /> {/* The Invisible Value */}
                </div>
              </div>
            )}

            {type === "keyboard" && (
              <div className="flex flex-col gap-4">
                <div className="w-full h-12 bg-white/5 rounded-lg border border-white/10 p-3">
                  <div className="w-1 h-full bg-emerald-500/40 animate-pulse" />
                </div>
                <div className="w-full h-32 bg-white/5 rounded-t-xl mt-auto grid grid-cols-4 gap-1 p-1">
                  {[...Array(12)].map((_, i) => (
                    <div key={i} className="bg-white/10 rounded-sm" />
                  ))}
                </div>
              </div>
            )}

            {type === "i18n" && (
              <div className="flex flex-col gap-4 items-center justify-center h-full">
                <div className="w-[120px] h-10 bg-emerald-500/20 rounded-lg border border-emerald-500/30 flex items-center justify-center px-2">
                  <div className="w-[160px] h-2 bg-white/20 rounded shrink-0" />
                </div>
              </div>
            )}

            {type === "phantom" && (
              <div className="flex flex-col gap-4 items-center justify-center h-full">
                <div className="w-48 h-12 bg-amber-500/10 rounded-xl border border-amber-500/20 flex items-center justify-center">
                  <div className="w-20 h-2 bg-amber-500/30 rounded" />
                </div>
                <div className="w-6 h-6 rounded-full border border-white/20 flex items-center justify-center">
                   <div className="w-2 h-2 bg-white/20 rounded-full" />
                </div>
              </div>
            )}

            {type === "dead-end" && (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-full h-full bg-white/5 rounded-xl border border-white/10" />
                <div className="absolute w-10 h-10 border-2 border-white/20 border-t-white/80 rounded-full animate-spin" />
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Grid Pattern Overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:10px_10px] pointer-events-none" />

      {/* Ghost Vision Annotations */}
      <div className="absolute inset-0 z-40 pointer-events-none">
        {renderAnnotation()}
      </div>

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
