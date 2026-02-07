"use client";

import { motion, AnimatePresence } from "framer-motion";
import { SimulationState } from "@/app/lab/page";
import { cn } from "@/lib/utils";
import { AlertCircle, Target, Search } from "lucide-react";

interface DeviceEmulatorProps {
  state: SimulationState;
  step: number;
  device: string;
}

export function DeviceEmulator({ state, step, device }: DeviceEmulatorProps) {
  const isIphone = device === "iphone-15" || device === "s23";
  const isScanning = state === "scanning";
  const isAnalyzing = state === "analyzing" || state === "complete";

  return (
    <div className="relative flex items-center justify-center h-full">
      {/* Device Frame */}
      <motion.div 
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 1, ease: "circOut" }}
        className={cn(
          "relative border-[8px] border-zinc-800 rounded-[3rem] shadow-2xl bg-zinc-900 overflow-hidden transition-all duration-700",
          isIphone ? "w-[320px] h-[640px]" : "w-full max-w-2xl h-[500px]"
        )}
      >
        {/* Notch/Camera Area */}
        {isIphone && (
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-32 h-6 bg-zinc-800 rounded-b-2xl z-30 flex items-center justify-center">
            <div className="w-12 h-1 bg-zinc-900 rounded-full" />
          </div>
        )}

        {/* Screen Content (Mock Website) */}
        <div className="absolute inset-0 bg-white z-10 p-6 flex flex-col gap-6 pt-12">
          <div className="flex items-center justify-between border-b border-zinc-100 pb-4">
            <div className="w-8 h-8 rounded bg-zinc-100" />
            <div className="w-32 h-4 bg-zinc-100 rounded-full" />
            <div className="w-8 h-8 rounded bg-zinc-100" />
          </div>
          
          <div className="space-y-4">
            <h2 className="text-2xl font-bold text-zinc-900 tracking-tight">Sign Up</h2>
            <p className="text-sm text-zinc-400">Join Orbit Apparel today.</p>
          </div>

          <div className="space-y-4">
            <div className="space-y-1">
              <div className="w-20 h-3 bg-zinc-100 rounded" />
              <div className="w-full h-12 bg-zinc-50 border border-zinc-200 rounded-lg" />
            </div>
            <div className="space-y-1 relative">
              <div className="w-20 h-3 bg-zinc-100 rounded" />
              <div className="w-full h-12 bg-zinc-50 border border-zinc-200 rounded-lg" />
              {/* Friction Node 1: Obscured Input */}
              <AnimatePresence>
                {step >= 3 && (
                  <motion.div 
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="absolute -right-4 -top-4 z-20 flex items-center gap-2"
                  >
                    <div className="w-8 h-8 rounded-full bg-red-500/20 border border-red-500/50 flex items-center justify-center animate-pulse">
                      <AlertCircle className="w-4 h-4 text-red-500" />
                    </div>
                    <div className="bg-red-500 text-white text-[8px] font-mono px-2 py-1 rounded shadow-lg uppercase whitespace-nowrap">
                      Obscured Input
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          <div className="mt-auto space-y-4 relative">
            <div className="w-full h-12 bg-emerald-500 rounded-lg flex items-center justify-center text-white font-bold text-sm">
              Create Account
            </div>
            {/* Friction Node 2: Low Contrast */}
            <AnimatePresence>
              {step >= 6 && (
                <motion.div 
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="absolute -left-4 -top-4 z-20 flex items-center gap-2"
                >
                  <div className="bg-amber-500 text-white text-[8px] font-mono px-2 py-1 rounded shadow-lg uppercase whitespace-nowrap">
                    Contrast Failure (1.2:1)
                  </div>
                  <div className="w-8 h-8 rounded-full bg-amber-500/20 border border-amber-500/50 flex items-center justify-center animate-pulse">
                    <Target className="w-4 h-4 text-amber-500" />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Neural Scan Overlay */}
        <AnimatePresence>
          {isScanning && (
            <motion.div 
              initial={{ top: "-10%" }}
              animate={{ top: "110%" }}
              exit={{ opacity: 0 }}
              transition={{ duration: 3, ease: "linear" }}
              className="absolute left-0 right-0 h-1 bg-emerald-500 shadow-[0_0_30px_rgba(16,185,129,1)] z-40"
            />
          )}
        </AnimatePresence>

        {/* Dimmer Overlay */}
        {state === "idle" && (
          <div className="absolute inset-0 bg-black/40 backdrop-blur-[2px] z-20 flex items-center justify-center">
            <div className="text-center space-y-2">
              <div className="w-12 h-12 rounded-full border border-emerald-500/30 bg-emerald-500/10 flex items-center justify-center mx-auto mb-4">
                <Search className="w-6 h-6 text-emerald-500" />
              </div>
              <p className="text-[10px] font-mono text-emerald-500/60 uppercase tracking-[0.2em]">Ready for Analysis</p>
            </div>
          </div>
        )}

        {/* Static/Noise overlay when analyzing */}
        {isAnalyzing && (
          <div className="absolute inset-0 z-30 pointer-events-none opacity-[0.03] bg-[url('https://grainy-gradients.vercel.app/noise.svg')]" />
        )}
      </motion.div>

      {/* Decorative Labels around the device */}
      <div className="absolute top-1/2 -left-20 -translate-y-1/2 flex flex-col gap-4 opacity-20">
        <div className="w-12 h-px bg-emerald-500" />
        <span className="text-[8px] font-mono rotate-90 uppercase tracking-widest text-emerald-500">Optical_Stream_v2.0</span>
      </div>
      <div className="absolute top-1/2 -right-20 -translate-y-1/2 flex flex-col gap-4 opacity-20">
        <div className="w-12 h-px bg-emerald-500" />
        <span className="text-[8px] font-mono -rotate-90 uppercase tracking-widest text-emerald-500">Neural_Feedback_Active</span>
      </div>
    </div>
  );
}
