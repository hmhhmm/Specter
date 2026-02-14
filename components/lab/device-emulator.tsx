"use client";

import { motion } from "framer-motion";
import { SimulationState } from "@/app/lab/page";
import { cn } from "@/lib/utils";
import { Camera, Video } from "lucide-react";

interface DeviceEmulatorProps {
  state: SimulationState;
  step: number;
  device: string;
  screenshot?: string | null;
  liveFrame?: string | null;
  isLiveMode?: boolean;
  onToggleLiveMode?: () => void;
}

export function DeviceEmulator({ 
  state, 
  step, 
  device, 
  screenshot, 
  liveFrame,
  isLiveMode = true,
  onToggleLiveMode
}: DeviceEmulatorProps) {
  const isIphone = device === "iphone-15" || device === "s23";
  const isRunning = state !== "idle";

  // Use live frame if in live mode (with screenshot as fallback), otherwise screenshot only
  const displayImage = isLiveMode ? (liveFrame || screenshot) : screenshot;
  const showingLiveFrame = isLiveMode && !!liveFrame;
  // Live mode is "on" but no frames yet — still connecting / waiting
  const liveConnecting = isLiveMode && !liveFrame && isRunning;

  return (
    <div className="relative flex items-start justify-center h-full gap-4 ">
      {/* Device Frame */}
      <motion.div 
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 1, ease: "circOut" }}
        className={cn(
          "relative rounded-[2rem] shadow-2xl bg-zinc-900 overflow-hidden transition-all duration-700 border-4 border-zinc-800",
          isIphone ? "w-[320px] h-[640px]" : "w-full max-w-2xl h-[500px]"
        )}
      >
        {/* Screen Content - Live Stream, Screenshot, or Mock */}
        {displayImage ? (
          <div className="absolute inset-0 bg-white z-10 flex items-center justify-center relative">
            <img 
              src={displayImage} 
              alt={isLiveMode ? "Live browser stream" : "Test screenshot"} 
              className="w-full h-full object-contain"
            />
          </div>
        ) : (
          <div className="absolute inset-0 bg-zinc-900 z-10 flex items-center justify-center">
            <p className="text-sm text-zinc-500">No preview available</p>
          </div>
        )}
        
      </motion.div>

      {/* Vertical Toggle Buttons */}
      {onToggleLiveMode && (
        <div className="flex flex-col gap-2 pt-2">
          <div className="relative">
            <button
              onClick={() => {
                if (!isLiveMode) {
                  onToggleLiveMode();
                }
              }}
              className={cn(
                "flex items-center justify-center p-2 rounded-lg text-[10px] font-mono uppercase tracking-wider transition-all",
                isLiveMode
                  ? "bg-red-500/20 text-red-400 border border-red-500/30"
                  : "text-zinc-500 hover:text-zinc-300 border border-white/5"
              )}
              title="Live View"
            >
              <Video className="w-4 h-4" />
            </button>
            {isLiveMode && isRunning && (
              <>
                <motion.span
                  animate={{ opacity: [1, 0.3, 1] }}
                  transition={{ duration: 1.2, repeat: Infinity }}
                  className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-red-400"
                />
                <span className="absolute -top-1 -right-10 text-[9px] text-red-400 font-bold uppercase tracking-wider whitespace-nowrap">
                  Live
                </span>
              </>
            )}
          </div>
          <button
            onClick={() => {
              if (isLiveMode) {
                onToggleLiveMode();
              }
            }}
            className={cn(
              "flex items-center justify-center p-2 rounded-lg text-[10px] font-mono uppercase tracking-wider transition-all",
              !isLiveMode
                ? "bg-white/5 text-zinc-300 border border-white/10"
                : "text-zinc-500 hover:text-zinc-300 border border-white/5"
            )}
            title="Screenshot History"
          >
            <Camera className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}
