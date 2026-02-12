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
  const isScanning = state === "scanning";
  const isAnalyzing = state === "analyzing" || state === "complete";
  const isRunning = state !== "idle";

  // Use live frame if in live mode (with screenshot as fallback), otherwise screenshot only
  const displayImage = isLiveMode ? (liveFrame || screenshot) : screenshot;
  const showingLiveFrame = isLiveMode && !!liveFrame;
  // Live mode is "on" but no frames yet — still connecting / waiting
  const liveConnecting = isLiveMode && !liveFrame && isRunning;

  return (
    <div className="relative flex flex-col items-center justify-center h-full gap-3">
      {/* ── Prominent toggle bar ── */}
      {onToggleLiveMode && (
        <div className="flex items-center gap-1 p-1 bg-zinc-900/80 border border-zinc-700/60 rounded-xl backdrop-blur-md shadow-lg z-50">
          <button
            onClick={() => {
              if (!isLiveMode) {
                // Switch TO live mode
                onToggleLiveMode();
              }
              // If already in live mode, clicking does nothing — user is already here
            }}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all",
              isLiveMode
                ? "bg-red-600 text-white shadow-md shadow-red-600/30"
                : "text-zinc-400 hover:text-white hover:bg-zinc-800"
            )}
          >
            <Video className="w-4 h-4" />
            Live View
            {isLiveMode && isRunning && (
              <motion.span
                animate={{ opacity: [1, 0.3, 1] }}
                transition={{ duration: 1.2, repeat: Infinity }}
                className="ml-1 w-2 h-2 rounded-full bg-white inline-block"
              />
            )}
          </button>
          <button
            onClick={() => {
              if (isLiveMode) {
                // Switch TO screenshot mode
                onToggleLiveMode();
              }
            }}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all",
              !isLiveMode
                ? "bg-emerald-600 text-white shadow-md shadow-emerald-600/30"
                : "text-zinc-400 hover:text-white hover:bg-zinc-800"
            )}
          >
            <Camera className="w-4 h-4" />
            Screenshot History
          </button>
        </div>
      )}

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

        {/* Screen Content - Live Stream, Screenshot, or Mock */}
        {displayImage ? (
          <div className="absolute inset-0 bg-white z-10 flex items-center justify-center relative">
            <img 
              src={displayImage} 
              alt={isLiveMode ? "Live browser stream" : "Test screenshot"} 
              className="w-full h-full object-contain"
            />
            
            {/* LIVE badge inside viewport */}
            {showingLiveFrame && isRunning && (
              <motion.div 
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                className="absolute top-4 left-4 px-3 py-1 bg-red-500 text-white text-xs font-bold rounded-full flex items-center gap-2 shadow-lg z-50"
              >
                <motion.div 
                  animate={{ opacity: [1, 0.3, 1] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                  className="w-2 h-2 bg-white rounded-full" 
                />
                LIVE
              </motion.div>
            )}

            {/* Connecting indicator when live mode is on but no frames yet */}
            {liveConnecting && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="absolute top-4 left-4 px-3 py-1 bg-yellow-600 text-white text-xs font-bold rounded-full flex items-center gap-2 shadow-lg z-50"
              >
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="w-3 h-3 border-2 border-white border-t-transparent rounded-full"
                />
                CONNECTING LIVE…
              </motion.div>
            )}
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
