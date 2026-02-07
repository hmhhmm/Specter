"use client";

import { motion, useMotionValue, useTransform, Variants } from "framer-motion";
import { Eye, TrendingDown, Code2, CheckCircle2, Zap, AlertTriangle, Cpu } from "lucide-react";
import { cn } from "@/lib/utils";
import { useEffect, useRef, useState } from "react";

const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.8,
      ease: [0.21, 0.45, 0.32, 0.9],
    },
  },
};

const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.25,
      delayChildren: 0.2,
    },
  },
};

const TypingCode = ({ text }: { text: string }) => {
  const [displayedText, setDisplayedText] = useState("");
  const [currentIndex, setCurrentIndex] = useState(0);
  const terminalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText((prev) => prev + text[currentIndex]);
        setCurrentIndex((prev) => prev + 1);
        if (terminalRef.current) {
          terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
        }
      }, 30);
      return () => clearTimeout(timeout);
    }
  }, [currentIndex, text]);

  return (
    <div className="relative mt-6 bg-black/80 rounded-xl p-5 font-mono text-[11px] leading-relaxed text-emerald-400/90 border border-emerald-500/20 h-[140px] overflow-hidden shadow-2xl">
      <div className="flex gap-2 mb-3 border-b border-white/5 pb-2">
        <div className="w-2.5 h-2.5 rounded-full bg-red-500/40" />
        <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/40" />
        <div className="w-2.5 h-2.5 rounded-full bg-green-500/40" />
        <span className="text-[9px] text-zinc-600 ml-2 uppercase tracking-widest">patch_engine.sh</span>
      </div>
      <pre className="whitespace-pre-wrap">
        <span className="text-zinc-500 mr-2">$</span>
        {displayedText}
        <span className="animate-pulse bg-emerald-500 text-transparent ml-1">|</span>
      </pre>
      <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-black to-transparent pointer-events-none" />
    </div>
  );
};

function FeatureCard({ 
  children, 
  title, 
  description, 
  icon: Icon, 
  accentColor = "emerald", 
  className 
}: { 
  children?: React.ReactNode; 
  title: string; 
  description: string; 
  icon: any; 
  accentColor?: "emerald" | "red" | "blue";
  className?: string;
}) {
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  function handleMouseMove({ currentTarget, clientX, clientY }: React.MouseEvent) {
    const { left, top } = currentTarget.getBoundingClientRect();
    mouseX.set(clientX - left);
    mouseY.set(clientY - top);
  }

  const accentHex = accentColor === "emerald" ? "#10b981" : accentColor === "red" ? "#ef4444" : "#3b82f6";
  const bgGradient = useTransform(
    [mouseX, mouseY],
    ([x, y]) => `radial-gradient(800px circle at ${x}px ${y}px, ${accentHex}20, transparent 40%)`
  );

  return (
    <motion.div
      variants={fadeInUp}
      onMouseMove={handleMouseMove}
      className={cn(
        "group relative p-10 rounded-[2rem] bg-zinc-900/40 border border-white/5 hover:border-white/10 transition-all duration-700 overflow-hidden flex flex-col h-full",
        className
      )}
    >
      <motion.div 
        className="absolute inset-0 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-700"
        style={{ background: bgGradient }}
      />
      
      {/* Background Icon Watermark */}
      <div className="absolute -top-12 -right-12 p-4 opacity-[0.03] group-hover:opacity-[0.08] transition-opacity duration-700 rotate-12 group-hover:rotate-0">
         <Icon className="w-64 h-64 text-white" />
      </div>

      <div className="relative z-10 flex flex-col h-full">
        <div className={cn(
          "w-16 h-16 rounded-2xl flex items-center justify-center mb-8 border transition-transform duration-500 group-hover:scale-110 group-hover:rotate-3 shadow-2xl",
          accentColor === "emerald" ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-500 shadow-emerald-500/10" : 
          accentColor === "red" ? "bg-red-500/10 border-red-500/20 text-red-500 shadow-red-500/10" :
          "bg-blue-500/10 border-blue-500/20 text-blue-500 shadow-blue-500/10"
        )}>
          <Icon className="w-8 h-8" />
        </div>

        <h3 className="text-3xl font-bold text-white mb-4 font-bricolage tracking-tight leading-none group-hover:translate-x-1 transition-transform duration-500">
          {title}
        </h3>
        
        <p className="text-zinc-400 text-lg mb-8 leading-relaxed font-light tracking-tight">
          {description}
        </p>

        <div className="mt-auto">
          {children}
        </div>
      </div>
    </motion.div>
  );
}

export function ProblemGrid() {
  return (
    <section id="features" className="relative py-32 bg-transparent overflow-hidden">
      {/* Decorative Orbs */}
      <div className="absolute top-1/2 left-0 -translate-y-1/2 w-[600px] h-[600px] bg-emerald-500/[0.08] blur-[120px] rounded-full pointer-events-none animate-pulse" />
      <div className="absolute bottom-0 right-0 w-[800px] h-[800px] bg-emerald-500/[0.08] blur-[120px] rounded-full pointer-events-none animate-pulse" style={{ animationDelay: '2s' }} />

      {/* Horizontal Data Beams */}
      <div className="absolute inset-0 pointer-events-none">
        <motion.div 
          animate={{ x: ["-100%", "100%"] }}
          transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
          className="absolute top-[20%] left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-emerald-500/25 to-transparent"
        />
        <motion.div 
          animate={{ x: ["100%", "-100%"] }}
          transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
          className="absolute top-[60%] left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-emerald-500/15 to-transparent"
        />
      </div>

      <div className="max-w-7xl mx-auto px-6">
        <motion.div 
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeInUp}
          className="text-center mb-24 relative"
        >
          <div className="inline-block px-4 py-1.5 mb-6 rounded-full bg-white/5 border border-white/10 text-[10px] font-mono text-zinc-500 uppercase tracking-[0.3em] backdrop-blur-sm">
            Diagnostic Matrix v1.0
          </div>
          <h2 className="font-bricolage text-4xl md:text-7xl font-bold text-white mb-6 tracking-tighter">
            Identifying the <span className="text-emerald-500">Silent</span> Killers
          </h2>
          <p className="text-zinc-500 font-mono text-base max-w-2xl mx-auto leading-relaxed">
            While traditional logs catch explicit errors, Specter’s vision-first agents detect the nuanced friction that kills conversion.
          </p>
        </motion.div>

        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={staggerContainer}
          className="grid grid-cols-1 lg:grid-cols-3 gap-8"
        >
          {/* Card 1: Visual Reasoning */}
          <FeatureCard
            title="Visual Reasoning"
            description="Our agents simulate human perception to find UX flaws that data alone can't explain."
            icon={Eye}
            accentColor="emerald"
          >
            <div className="relative h-40 bg-zinc-950/50 rounded-2xl border border-white/5 overflow-hidden group/scan shadow-inner">
               {/* Mock UI Sketch */}
               <div className="absolute inset-4 space-y-3 opacity-20">
                  <div className="h-4 w-3/4 bg-zinc-800 rounded-full" />
                  <div className="h-24 w-full bg-zinc-800/50 rounded-lg" />
                  <div className="flex gap-2">
                    <div className="h-8 w-1/2 bg-zinc-800 rounded-lg" />
                    <div className="h-8 w-1/2 bg-zinc-800 rounded-lg" />
                  </div>
               </div>
               {/* Scan Line */}
               <motion.div 
                animate={{ top: ["-10%", "110%", "-10%"] }}
                transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                className="absolute left-0 right-0 h-0.5 bg-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.8)] z-20"
               />
               <div className="absolute inset-0 bg-gradient-to-b from-emerald-500/5 via-transparent to-emerald-500/5 opacity-0 group-hover/scan:opacity-100 transition-opacity duration-700" />
               <div className="absolute bottom-4 left-4 flex items-center gap-2">
                  <Cpu className="w-3 h-3 text-emerald-500 animate-pulse" />
                  <span className="text-[9px] font-mono text-emerald-500/60 uppercase tracking-widest">Neural Scan Active</span>
               </div>
            </div>
          </FeatureCard>

          {/* Card 2: Revenue Leak */}
          <FeatureCard
            title="Revenue Leakage"
            description="Identifies the precise moment users drop out and calculates the real dollar impact."
            icon={TrendingDown}
            accentColor="red"
          >
            <div className="p-6 bg-black/40 rounded-2xl border border-red-500/10 shadow-inner">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <p className="text-[10px] font-mono text-zinc-600 uppercase tracking-widest mb-1">Impact Velocity</p>
                  <motion.p 
                    animate={{ scale: [1, 1.05, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="text-3xl font-bold text-red-500 font-bricolage"
                  >
                    $42,850<span className="text-sm font-normal text-red-500/50">/mo</span>
                  </motion.p>
                </div>
                <div className="p-2 bg-red-500/10 rounded-lg border border-red-500/20">
                  <AlertTriangle className="w-4 h-4 text-red-500" />
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-[10px] font-mono text-zinc-500">
                  <span>Checkout Friction</span>
                  <span className="text-red-400">Critical</span>
                </div>
                <div className="h-2 w-full bg-zinc-800/50 rounded-full overflow-hidden p-[2px]">
                  <motion.div 
                    initial={{ width: 0 }}
                    whileInView={{ width: "85%" }}
                    transition={{ duration: 2, ease: "circOut" }}
                    className="h-full bg-gradient-to-r from-red-600 to-red-400 rounded-full relative shadow-[0_0_10px_rgba(239,68,68,0.4)]"
                  >
                    <motion.div 
                      animate={{ opacity: [0.4, 1, 0.4], x: ["-100%", "200%"] }}
                      transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                      className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                    />
                  </motion.div>
                </div>
              </div>
            </div>
          </FeatureCard>

          {/* Card 3: Self-Healing */}
          <FeatureCard
            title="Autonomous Fixes"
            description="Specter doesn't just report—it autonomously drafts and tests patches for UI regressions."
            icon={Code2}
            accentColor="emerald"
          >
            <TypingCode text={`// Resolving hydration mismatch\nconst safeValue = useSafeHydration(val);\n\n// Patching layout overflow\nstyle.overflow = 'hidden-visual';\n\n// Verified by GhostAgent v4.2`} />
          </FeatureCard>
        </motion.div>

        {/* Bottom Callout */}
        <motion.div 
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="mt-20 flex flex-col items-center justify-center text-center space-y-4"
        >
          <div className="flex -space-x-3">
             {[1,2,3,4].map(i => (
               <div key={i} className="w-10 h-10 rounded-full border-2 border-zinc-950 bg-zinc-800 flex items-center justify-center overflow-hidden">
                 <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${i + 10}`} alt="Agent Avatar" />
               </div>
             ))}
             <div className="w-10 h-10 rounded-full border-2 border-zinc-950 bg-emerald-500 flex items-center justify-center text-[10px] font-bold text-black">
               +12
             </div>
          </div>
          <p className="text-zinc-600 font-mono text-xs uppercase tracking-[0.2em]">Active Sentinel Agents Monitoring Global Flows</p>
        </motion.div>
      </div>
    </section>
  );
}
