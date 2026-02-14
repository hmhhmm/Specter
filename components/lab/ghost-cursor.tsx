"use client";

import { motion, useSpring, useMotionValue } from "framer-motion";
import { useEffect } from "react";
import { MousePointer2 } from "lucide-react";

interface GhostCursorProps {
  x: number;
  y: number;
  isActive: boolean;
}

export function GhostCursor({ x, y, isActive }: GhostCursorProps) {
  // Use springs for smooth, natural movement
  const springX = useSpring(x, { damping: 40, stiffness: 200 });
  const springY = useSpring(y, { damping: 40, stiffness: 200 });

  useEffect(() => {
    springX.set(x);
    springY.set(y);
  }, [x, y, springX, springY]);

  if (!isActive) return null;

  return (
    <motion.div
      style={{
        left: springX,
        top: springY,
        position: "absolute",
        zIndex: 1000,
        pointerEvents: "none",
      }}
      initial={{ opacity: 0, scale: 0.5 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.5 }}
    >
      <div className="relative">
        {/* The Cursor Icon */}
        <MousePointer2 className="w-6 h-6 text-emerald-500 fill-emerald-500/30 drop-shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
        
        {/* Glow Effect */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-12 h-12 bg-emerald-500/20 rounded-full blur-xl" />
        
        {/* Label (Optional, for "AI" identification) */}
        <div className="absolute left-full top-0 ml-2 px-1.5 py-0.5 rounded bg-emerald-500 text-black text-[8px] font-bold uppercase tracking-widest whitespace-nowrap shadow-lg">
          Ghost AI
        </div>
      </div>
    </motion.div>
  );
}
