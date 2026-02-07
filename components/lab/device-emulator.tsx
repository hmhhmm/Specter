"use client";

import { motion, AnimatePresence } from "framer-motion";
import { SimulationState } from "@/app/lab/page";
import { cn } from "@/lib/utils";
import { AlertCircle, Target, Search, MessageSquare, AlertTriangle, Eye, Type, Globe, RefreshCw } from "lucide-react";
import { GhostCursor } from "./ghost-cursor";
import { useRef, useEffect } from "react";

interface DeviceEmulatorProps {
  state: SimulationState;
  step: number;
  device: string;
}

// Map steps to screen coordinates (percentages)
const ISSUE_COORDINATES = [
  { x: "50%", y: "20%" }, // Initial Scan (Step 0)
  { x: "80%", y: "88%" }, // Issue 1: Z-Index Trap (Step 1)
  { x: "40%", y: "28%" }, // Issue 2: Data Overflow (Step 2)
  { x: "70%", y: "62%" }, // Issue 3: Invisible Fee (Step 3)
  { x: "70%", y: "52%" }, // Issue 4: Rage Input (Step 4)
  { x: "70%", y: "68%" }, // Issue 5: Localization Break (Step 5)
  { x: "70%", y: "78%" }, // Issue 6: Phantom Error (Step 6)
  { x: "50%", y: "50%" }, // Issue 7: Dead-End Spinner (Step 7)
  { x: "50%", y: "50%" }, // Completion (Step 8)
];

export function DeviceEmulator({ state, step, device }: DeviceEmulatorProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const isIphone = device === "iphone-15" || device === "s23";
  const isScanning = state === "scanning";
  const isAnalyzing = state === "analyzing" || state === "complete";

  // Coordinates for current step
  const currentPos = ISSUE_COORDINATES[step] || { x: "50%", y: "50%" };

  // Handle iframe interaction based on step
  useEffect(() => {
    if (!iframeRef.current) return;

    // 1. Handle Scrolling
    if (step >= 4) {
      iframeRef.current.contentWindow?.scrollTo({
        top: 300,
        behavior: "smooth"
      });
    } else {
      iframeRef.current.contentWindow?.scrollTo({
        top: 0,
        behavior: "smooth"
      });
    }

    // 2. Handle Localization Switch (Step 5)
    if (step === 5) {
      iframeRef.current.contentWindow?.postMessage({ type: 'SET_LANG', lang: 'de' }, '*');
    }

    // 3. Handle Dead-End Spinner (Step 7)
    if (step === 7) {
      iframeRef.current.contentWindow?.postMessage({ type: 'SHOW_SPINNER' }, '*');
    }
  }, [step]);

  return (
    <div className="relative flex items-center justify-center h-full">
      {/* Device Frame */}
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 1, ease: "circOut" }}
        className={cn(
          "relative border-[12px] border-zinc-800 rounded-[3.5rem] shadow-2xl bg-zinc-900 overflow-hidden transition-all duration-700 max-h-full",
          isIphone ? "aspect-[9/19.5] h-full w-auto" : "aspect-video w-full h-auto max-w-4xl",
        )}
      >
        {/* Notch/Camera Area */}
        {isIphone && (
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-32 h-7 bg-zinc-800 rounded-b-3xl z-50 flex items-center justify-center">
            <div className="w-12 h-1.5 bg-zinc-900 rounded-full" />
          </div>
        )}

        {/* The Glass Layer (External Annotations) */}
        <div className="absolute inset-0 z-40 pointer-events-none">
          {/* 1. Ghost AI Cursor */}
          <AnimatePresence>
            {isAnalyzing && (
              <GhostCursor 
                x={parseFloat(currentPos.x.replace('%', '')) * (isIphone ? 3.6 : 8.9)} 
                y={parseFloat(currentPos.y.replace('%', '')) * (isIphone ? 7.2 : 6.0)}
                isActive={isAnalyzing && step > 0} 
              />
            )}
          </AnimatePresence>

          {/* 2. Scanning Effect */}
          <AnimatePresence>
            {isScanning && (
              <motion.div
                initial={{ top: "-10%" }}
                animate={{ top: "110%" }}
                exit={{ opacity: 0 }}
                transition={{ duration: 3, ease: "linear" }}
                className="absolute left-0 right-0 h-1 bg-emerald-500 shadow-[0_0_30px_rgba(16,185,129,1)] z-50"
              />
            )}
          </AnimatePresence>

          {/* 3. Issue Annotations (Glass Layer) */}
          <AnimatePresence>
            {step === 1 && (
              <motion.div initial={{ opacity: 0, scale: 0.5 }} animate={{ opacity: 1, scale: 1 }} className="absolute bottom-16 right-8 p-4 bg-red-500 border border-red-400 rounded-xl shadow-2xl flex items-center gap-3">
                <MessageSquare className="w-5 h-5 text-white" />
                <div className="text-white">
                   <p className="text-[10px] font-bold uppercase tracking-widest">Z-Index Trap</p>
                   <p className="text-[8px] opacity-80">Element Obscured: Trade Button</p>
                </div>
              </motion.div>
            )}
            {step === 2 && (
              <motion.div initial={{ opacity: 0, scale: 0.5 }} animate={{ opacity: 1, scale: 1 }} className="absolute top-32 left-8 p-4 bg-red-500 border border-red-400 rounded-xl shadow-2xl flex items-center gap-3">
                <AlertTriangle className="w-5 h-5 text-white" />
                <div className="text-white">
                   <p className="text-[10px] font-bold uppercase tracking-widest">Data Overflow</p>
                   <p className="text-[8px] opacity-80">Price exceeds container bounds</p>
                </div>
              </motion.div>
            )}
            {step === 3 && (
              <motion.div initial={{ opacity: 0, scale: 0.5 }} animate={{ opacity: 1, scale: 1 }} className="absolute top-[60%] right-8 p-4 bg-amber-500 border border-amber-400 rounded-xl shadow-2xl flex items-center gap-3">
                <Eye className="w-5 h-5 text-white" />
                <div className="text-white">
                   <p className="text-[10px] font-bold uppercase tracking-widest">Invisible Fee</p>
                   <p className="text-[8px] opacity-80">Fee value hidden: $2.50 unreadable</p>
                </div>
              </motion.div>
            )}
            {step === 4 && (
              <motion.div initial={{ opacity: 0, scale: 0.5 }} animate={{ opacity: 1, scale: 1 }} className="absolute top-[45%] left-8 p-4 bg-blue-500 border border-blue-400 rounded-xl shadow-2xl flex items-center gap-3">
                <Type className="w-5 h-5 text-white" />
                <div className="text-white">
                   <p className="text-[10px] font-bold uppercase tracking-widest">Keyboard Mismatch</p>
                   <p className="text-[8px] opacity-80">Amount input triggers ABC not 123</p>
                </div>
              </motion.div>
            )}
            {step === 5 && (
              <motion.div initial={{ opacity: 0, scale: 0.5 }} animate={{ opacity: 1, scale: 1 }} className="absolute top-[62%] right-8 p-4 bg-red-500 border border-red-400 rounded-xl shadow-2xl flex items-center gap-3">
                <Globe className="w-5 h-5 text-white" />
                <div className="text-white">
                   <p className="text-[10px] font-bold uppercase tracking-widest">Text Overflow</p>
                   <p className="text-[8px] opacity-80">German text exceeds button width</p>
                </div>
              </motion.div>
            )}
            {step === 6 && (
              <motion.div initial={{ opacity: 0, scale: 0.5 }} animate={{ opacity: 1, scale: 1 }} className="absolute top-[78%] left-8 p-4 bg-red-600 border border-red-400 rounded-xl shadow-2xl flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-white" />
                <div className="text-white">
                   <p className="text-[10px] font-bold uppercase tracking-widest">Silent Failure</p>
                   <p className="text-[8px] opacity-80">Withdraw: No feedback on click</p>
                </div>
              </motion.div>
            )}
            {step === 7 && (
              <motion.div initial={{ opacity: 0, scale: 0.5 }} animate={{ opacity: 1, scale: 1 }} className="absolute inset-0 bg-red-950/20 backdrop-blur-sm flex items-center justify-center">
                 <div className="p-6 bg-red-600 rounded-3xl shadow-2xl text-center space-y-2 border border-red-400">
                    <RefreshCw className="w-8 h-8 text-white animate-spin mx-auto mb-2" />
                    <p className="text-xs font-bold uppercase tracking-[0.2em]">Dead-End Spinner</p>
                    <p className="text-[10px] opacity-80">Global overlay blocking all input</p>
                 </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* The Iframe (Target Site) */}
        <iframe 
          ref={iframeRef}
          src="/mock-target" 
          className="absolute inset-0 w-full h-full border-none z-10 bg-black"
          title="Target Application"
        />

        {/* Dimmer Overlay (Idle State) */}
        {state === "idle" && (
          <div className="absolute inset-0 bg-black/60 backdrop-blur-[4px] z-50 flex items-center justify-center">
            <div className="text-center space-y-2">
              <div className="w-16 h-16 rounded-full border border-emerald-500/30 bg-emerald-500/10 flex items-center justify-center mx-auto mb-6">
                <Search className="w-8 h-8 text-emerald-500" />
              </div>
              <p className="text-xs font-mono text-emerald-500 uppercase tracking-[0.3em]">
                Initializing Ghost Link
              </p>
            </div>
          </div>
        )}

        {/* Static Noise Overlay */}
        {isAnalyzing && (
          <div className="absolute inset-0 z-30 pointer-events-none opacity-[0.02] bg-[url('https://grainy-gradients.vercel.app/noise.svg')]" />
        )}
      </motion.div>

      {/* Side Decorative Data Labels */}
      <div className="absolute top-1/2 -left-24 -translate-y-1/2 flex flex-col gap-4 opacity-30">
        <div className="w-16 h-[1px] bg-emerald-500" />
        <span className="text-[9px] font-mono rotate-90 uppercase tracking-widest text-emerald-500">
          Stream_Neural_Link_v4.2
        </span>
      </div>
      <div className="absolute top-1/2 -right-24 -translate-y-1/2 flex flex-col gap-4 opacity-30">
        <div className="w-16 h-[1px] bg-emerald-500" />
        <span className="text-[9px] font-mono -rotate-90 uppercase tracking-widest text-emerald-500">
          Ghost_Analysis_Active
        </span>
      </div>
    </div>
  );
}

