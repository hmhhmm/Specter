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

      <div className="max-w-7xl mx-auto px-6">
        <motion.div 
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeInUp}
          className="text-center mb-24 relative"
        >

          <h2 className="font-bricolage text-4xl md:text-6xl font-bold text-white mb-6 tracking-tighter">
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
            <div className="relative h-32 bg-zinc-950/50 rounded-xl border border-emerald-500/10 flex items-center justify-center">
               <div className="flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-emerald-500" />
                  <span className="text-xs font-mono text-emerald-500/80 uppercase tracking-wider">Neural Scan Active</span>
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
            <div className="p-6 bg-black/40 rounded-xl border border-red-500/10">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-mono text-zinc-600 uppercase mb-1">Impact</p>
                  <p className="text-2xl font-bold text-red-500 font-bricolage">$42,850<span className="text-sm text-red-500/50">/mo</span></p>
                </div>
                <AlertTriangle className="w-5 h-5 text-red-500" />
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
            <div className="p-4 bg-black/80 rounded-xl border border-emerald-500/20 font-mono">
              <div className="flex items-center gap-2 mb-2 pb-2 border-b border-white/5">
                <div className="flex gap-1.5">
                  <div className="w-2 h-2 rounded-full bg-red-500/40" />
                  <div className="w-2 h-2 rounded-full bg-yellow-500/40" />
                  <div className="w-2 h-2 rounded-full bg-green-500/40" />
                </div>
                <span className="text-[10px] text-zinc-600 uppercase">patch_engine.sh</span>
              </div>
              <p className="text-xs text-emerald-400/90">
                <span className="text-zinc-500">$</span> Resolving hydration mismatch<br/>
                <span className="text-zinc-500">$</span> Patching layout overflow
              </p>
            </div>
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
