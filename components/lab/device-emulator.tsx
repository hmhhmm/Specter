"use client";

import { motion } from "framer-motion";
import { SimulationState } from "@/app/lab/page";
import { cn } from "@/lib/utils";

interface DeviceEmulatorProps {
  state: SimulationState;
  step: number;
  device: string;
  screenshot?: string | null;
}

export function DeviceEmulator({ state, step, device, screenshot }: DeviceEmulatorProps) {
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

        {/* Screen Content - Real Screenshot or Mock */}
        {screenshot ? (
          <div className="absolute inset-0 bg-white z-10 flex items-center justify-center">
            <img 
              src={screenshot} 
              alt="Live test screenshot" 
              className="w-full h-full object-contain"
            />
          </div>
        ) : (
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
            <div className="space-y-1">
              <div className="w-20 h-3 bg-zinc-100 rounded" />
              <div className="w-full h-12 bg-zinc-50 border border-zinc-200 rounded-lg" />
            </div>
          </div>

          <div className="mt-auto space-y-4">
            <div className="w-full h-12 bg-emerald-500 rounded-lg flex items-center justify-center text-white font-bold text-sm">
              Create Account
            </div>
          </div>
        </div>
        )}
        
        {/* Scan Overlay */}
        {isScanning && (
          <motion.div 
            initial={{ top: "-10%" }}
            animate={{ top: "110%" }}
            transition={{ duration: 3, ease: "linear" }}
            className="absolute left-0 right-0 h-1 bg-emerald-500 z-40"
          />
        )}

        {/* Dimmer Overlay */}
        {state === "idle" && (
          <div className="absolute inset-0 bg-black/40 backdrop-blur-[2px] z-20 flex items-center justify-center">
            <div className="text-center space-y-2">
              <p className="text-sm text-zinc-400">Ready</p>
            </div>
          </div>
        )}

      </motion.div>
    </div>
  );
}
