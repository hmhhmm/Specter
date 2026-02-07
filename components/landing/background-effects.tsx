"use client";

import { motion, useSpring, useMotionValue, useTransform, AnimatePresence } from "framer-motion";
import { useEffect, useState, useRef } from "react";

export function BackgroundEffects() {
  const [mounted, setMounted] = useState(false);
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const containerRef = useRef<HTMLDivElement>(null);

  // Smooth mouse tracking for parallax
  const springX = useSpring(mouseX, { damping: 50, stiffness: 300 });
  const springY = useSpring(mouseY, { damping: 50, stiffness: 300 });

  // Parallax offsets for different layers
  const gridX = useTransform(springX, (val) => (val - (typeof window !== 'undefined' ? window.innerWidth / 2 : 0)) * -0.015);
  const gridY = useTransform(springY, (val) => (val - (typeof window !== 'undefined' ? window.innerHeight / 2 : 0)) * -0.015);
  
  const bloomX = useTransform(springX, (val) => (val - (typeof window !== 'undefined' ? window.innerWidth / 2 : 0)) * 0.04);
  const bloomY = useTransform(springY, (val) => (val - (typeof window !== 'undefined' ? window.innerHeight / 2 : 0)) * 0.04);

  useEffect(() => {
    setMounted(true);
    const handleMouseMove = (e: MouseEvent) => {
      mouseX.set(e.clientX);
      mouseY.set(e.clientY);
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, [mouseX, mouseY]);

  if (!mounted) return <div className="fixed inset-0 bg-zinc-950 z-0" />;

  return (
    <div ref={containerRef} className="fixed inset-0 z-0 pointer-events-none overflow-hidden bg-[#050505]">
      {/* 1. The Sentinel Pulse (Atmospheric Breathing) */}
      <motion.div 
        animate={{ opacity: [0.05, 0.15, 0.05] }}
        transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
        className="absolute inset-0 bg-emerald-500/20 blur-[160px] mix-blend-screen"
      />

      {/* 2. Primary Interactive Bloom (The "Prominent Glow") */}
      <motion.div
        className="absolute w-[1600px] h-[1600px] rounded-full mix-blend-plus-lighter"
        style={{
          left: springX,
          top: springY,
          x: "-50%",
          y: "-50%",
          background: "radial-gradient(circle, rgba(16, 185, 129, 0.2) 0%, rgba(16, 185, 129, 0.05) 35%, transparent 75%)",
        }}
      />

      {/* 3. Deep Parallax Layer (Neural Architecture) */}
      <motion.div 
        style={{ x: gridX, y: gridY }}
        className="absolute inset-[-15%]"
      >
        {/* Major Grid Lines */}
        <div 
          className="absolute inset-0 opacity-[0.4]"
          style={{
            backgroundImage: `
              linear-gradient(to right, rgba(16, 185, 129, 0.2) 1px, transparent 1px),
              linear-gradient(to bottom, rgba(16, 185, 129, 0.2) 1px, transparent 1px)
            `,
            backgroundSize: "100px 100px",
            maskImage: "radial-gradient(circle at center, black, transparent 85%)"
          }}
        />
        
        {/* Neural Nodes (Pulsing intersection points) */}
        <div 
          className="absolute inset-0 opacity-[0.8]"
          style={{
            backgroundImage: `radial-gradient(circle at 1px 1px, rgba(16, 185, 129, 0.6) 1px, transparent 0)`,
            backgroundSize: "100px 100px",
          }}
        />

        {/* Dynamic Nodes (Randomly appearing/disappearing) */}
        {[...Array(6)].map((_, i) => (
          <DynamicNode key={i} />
        ))}
      </motion.div>

      {/* 4. Floating Ambient Orbs */}
      <motion.div
        style={{ x: bloomX, y: bloomY }}
        className="absolute inset-0 opacity-60"
      >
        <div className="absolute top-[15%] left-[10%] w-[500px] h-[500px] bg-emerald-500/15 blur-[120px] rounded-full animate-pulse" />
        <div className="absolute bottom-[20%] right-[5%] w-[600px] h-[600px] bg-emerald-600/10 blur-[140px] rounded-full animate-pulse" style={{ animationDelay: '3s' }} />
      </motion.div>

      {/* 5. Luxury Grain Overlay */}
      <div className="absolute inset-0 opacity-[0.025] mix-blend-overlay pointer-events-none bg-[url('https://grainy-gradients.vercel.app/noise.svg')]" />

      {/* 6. Ghost Data Streams */}
      <div className="absolute inset-0">
        {[...Array(25)].map((_, i) => (
          <GhostStream key={i} />
        ))}
      </div>

      {/* 7. Scanning Data Pulse (Horizontal) */}
      <div className="absolute inset-0 pointer-events-none opacity-[0.05]">
        <motion.div 
          animate={{ x: ["-100%", "200%"] }}
          transition={{ duration: 12, repeat: Infinity, ease: "linear", delay: 2 }}
          className="w-[300px] h-full bg-gradient-to-r from-transparent via-emerald-500/10 to-transparent skew-x-12"
        />
      </div>

      {/* 8. Mission Control Scanline (Vertical) */}
      <div className="absolute inset-0 pointer-events-none opacity-[0.04]">
        <motion.div 
          animate={{ y: ["-10%", "110%"] }}
          transition={{ duration: 18, repeat: Infinity, ease: "linear" }}
          className="h-[1px] w-full bg-gradient-to-r from-transparent via-emerald-400 to-transparent shadow-[0_0_15px_rgba(16,185,129,0.4)]"
        />
      </div>

      {/* 9. Depth & Vignette */}
      <div className="absolute inset-0 bg-gradient-to-b from-zinc-950/20 via-transparent to-zinc-950" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,rgba(0,0,0,0.4)_100%)]" />
    </div>
  );
}

function DynamicNode() {
  const [pos, setPos] = useState({ top: "0%", left: "0%" });
  const [active, setActive] = useState(false);

  useEffect(() => {
    const cycle = () => {
      setPos({
        top: Math.floor(Math.random() * 10) * 10 + "%",
        left: Math.floor(Math.random() * 10) * 10 + "%"
      });
      setActive(true);
      setTimeout(() => setActive(false), 2000);
      setTimeout(cycle, Math.random() * 10000 + 5000);
    };
    cycle();
  }, []);

  return (
    <motion.div
      animate={{ opacity: active ? [0, 1, 0] : 0, scale: active ? [0.5, 1.5, 0.5] : 0.5 }}
      transition={{ duration: 2, ease: "easeInOut" }}
      className="absolute w-2 h-2 bg-emerald-500/40 rounded-full blur-[2px]"
      style={{ top: pos.top, left: pos.left, x: "-50%", y: "-50%" }}
    />
  );
}

function GhostStream() {
  const [coords, setCoords] = useState<{ x: string; y: string; delay: number; duration: number; width: number } | null>(null);

  useEffect(() => {
    setCoords({
      x: Math.random() * 100 + "%",
      y: Math.random() * 100 + "%",
      delay: Math.random() * 15,
      duration: Math.random() * 10 + 10,
      width: Math.random() > 0.8 ? 2 : 1
    });
  }, []);

  if (!coords) return null;

  return (
    <motion.div
      className="absolute bg-gradient-to-b from-transparent via-emerald-500/40 to-transparent"
      style={{ width: coords.width, height: 80, x: coords.x, top: "-10%", opacity: 0 }}
      animate={{
        y: ["-10vh", "110vh"],
        opacity: [0, 0.7, 0]
      }}
      transition={{
        duration: coords.duration,
        repeat: Infinity,
        ease: "linear",
        delay: coords.delay
      }}
    />
  );
}
