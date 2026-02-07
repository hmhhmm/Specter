"use client";

import { motion } from "framer-motion";
import {
  User,
  Briefcase,
  ShoppingCart,
  Smartphone,
  Monitor,
  Signal,
  SignalLow,
  Wifi,
  Volume2,
  VolumeX,
  Play,
  RotateCcw,
  Target,
  FileText,
} from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { GlowButton } from "@/components/ui/glow-button";
import { SimulationState } from "@/app/lab/page";
import { cn } from "@/lib/utils";

interface ControlDeckProps {
  state: SimulationState;
  onStart: () => void;
  onReset: () => void;
  persona: string;
  setPersona: (v: string) => void;
  device: string;
  setDevice: (v: string) => void;
  network: string;
  setNetwork: (v: string) => void;
  isVoiceEnabled: boolean;
  setIsVoiceEnabled: (v: boolean) => void;
  targetUrl: string;
  setTargetUrl: (v: string) => void;
  objective: string;
  setObjective: (v: string) => void;
}

export function ControlDeck({
  state,
  onStart,
  onReset,
  persona,
  setPersona,
  device,
  setDevice,
  network,
  setNetwork,
  isVoiceEnabled,
  setIsVoiceEnabled,
  targetUrl,
  setTargetUrl,
  objective,
  setObjective,
}: ControlDeckProps) {
  const isRunning = state !== "idle" && state !== "complete";

  return (
    <motion.div
      initial={{ y: 100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: 0.5, duration: 0.8 }}
      className="fixed bottom-12 left-1/2 -translate-x-1/2 z-40 w-full max-w-7xl px-6"
    >
      <div
        className={cn(
          "relative rounded-[2.5rem] border border-white/10 bg-zinc-950/80 backdrop-blur-3xl px-8 py-5 shadow-2xl transition-all duration-500 flex flex-col gap-6",
          isRunning ? "border-emerald-500/30 shadow-emerald-500/10" : "",
        )}
      >
        <div className="flex items-center justify-between w-full gap-8">
          {/* Mission Briefing Section */}
          <div className="flex-1 flex items-center gap-6">
            <div className="flex-1 space-y-1.5">
              <div className="flex items-center gap-2 ml-1">
                <Target className="w-2.5 h-2.5 text-emerald-500" />
                <Label className="text-[9px] font-mono uppercase tracking-[0.2em] text-zinc-500">
                  Target URL
                </Label>
              </div>
              <input
                type="text"
                value={targetUrl}
                onChange={(e) => setTargetUrl(e.target.value)}
                disabled={isRunning}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2 font-mono text-[11px] text-emerald-500 focus:outline-none focus:border-emerald-500/50 transition-colors placeholder:text-zinc-700"
                placeholder="e.g. example.com/dashboard"
              />
            </div>
            <div className="flex-[1.5] space-y-1.5">
              <div className="flex items-center gap-2 ml-1">
                <FileText className="w-2.5 h-2.5 text-emerald-500" />
                <Label className="text-[9px] font-mono uppercase tracking-[0.2em] text-zinc-500">
                  Mission Objective
                </Label>
              </div>
              <input
                type="text"
                value={objective}
                onChange={(e) => setObjective(e.target.value)}
                disabled={isRunning}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2 font-mono text-[11px] text-zinc-300 focus:outline-none focus:border-emerald-500/50 transition-colors placeholder:text-zinc-700 italic"
                placeholder="Describe what to test..."
              />
            </div>
          </div>

          <div className="h-10 w-px bg-white/10" />

          {/* Configuration Section */}
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-4">
              <div className="space-y-1">
                <Label className="text-[9px] font-mono uppercase tracking-[0.2em] text-zinc-500 ml-1">
                  Persona
                </Label>
                <Select
                  value={persona}
                  onValueChange={setPersona}
                  disabled={isRunning}
                >
                  <SelectTrigger className="w-[150px] bg-white/5 border-white/10 rounded-xl font-mono text-[10px] h-9">
                    <SelectValue placeholder="Select Persona" />
                  </SelectTrigger>
                  <SelectContent className="bg-zinc-900 border-white/10 rounded-xl">
                    <SelectItem
                      value="senior"
                      className="focus:bg-emerald-500/20 focus:text-white text-[10px]"
                    >
                      <div className="flex items-center gap-2">
                        <User className="w-3 h-3" />
                        <span>Tech-Illiterate Senior</span>
                      </div>
                    </SelectItem>
                    <SelectItem
                      value="pro"
                      className="focus:bg-emerald-500/20 focus:text-white text-[10px]"
                    >
                      <div className="flex items-center gap-2">
                        <Briefcase className="w-3 h-3" />
                        <span>Impatient Pro</span>
                      </div>
                    </SelectItem>
                    <SelectItem
                      value="casual"
                      className="focus:bg-emerald-500/20 focus:text-white text-[10px]"
                    >
                      <div className="flex items-center gap-2">
                        <ShoppingCart className="w-3 h-3" />
                        <span>Casual Shopper</span>
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-1">
                <Label className="text-[9px] font-mono uppercase tracking-[0.2em] text-zinc-500 ml-1">
                  Device
                </Label>
                <Select
                  value={device}
                  onValueChange={setDevice}
                  disabled={isRunning}
                >
                  <SelectTrigger className="w-[130px] bg-white/5 border-white/10 rounded-xl font-mono text-[10px] h-9">
                    <SelectValue placeholder="Select Device" />
                  </SelectTrigger>
                  <SelectContent className="bg-zinc-900 border-white/10 rounded-xl">
                    <SelectItem
                      value="iphone-15"
                      className="focus:bg-emerald-500/20 focus:text-white text-[10px]"
                    >
                      <div className="flex items-center gap-2">
                        <Smartphone className="w-3 h-3" />
                        <span>iPhone 15 Pro</span>
                      </div>
                    </SelectItem>
                    <SelectItem
                      value="s23"
                      className="focus:bg-emerald-500/20 focus:text-white text-[10px]"
                    >
                      <div className="flex items-center gap-2">
                        <Smartphone className="w-3 h-3" />
                        <span>Samsung S23</span>
                      </div>
                    </SelectItem>
                    <SelectItem
                      value="desktop"
                      className="focus:bg-emerald-500/20 focus:text-white text-[10px]"
                    >
                      <div className="flex items-center gap-2">
                        <Monitor className="w-3 h-3" />
                        <span>Desktop Chrome</span>
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="h-8 w-px bg-white/5" />

            {/* Network Section */}
            <div className="space-y-1">
              <Label className="text-[9px] font-mono uppercase tracking-[0.2em] text-zinc-500 ml-1">
                Network
              </Label>
              <ToggleGroup
                type="single"
                value={network}
                onValueChange={(v) => v && setNetwork(v)}
                disabled={isRunning}
                className="bg-white/5 p-1 rounded-xl border border-white/10"
              >
                <ToggleGroupItem
                  value="5g"
                  className="rounded-lg data-[state=on]:bg-emerald-500/20 data-[state=on]:text-emerald-500 h-7 px-2"
                >
                  <Signal className="w-3 h-3" />
                </ToggleGroupItem>
                <ToggleGroupItem
                  value="4g"
                  className="rounded-lg data-[state=on]:bg-emerald-500/20 data-[state=on]:text-emerald-500 h-7 px-2"
                >
                  <SignalLow className="w-3 h-3" />
                </ToggleGroupItem>
                <ToggleGroupItem
                  value="3g"
                  className="rounded-lg data-[state=on]:bg-emerald-500/20 data-[state=on]:text-emerald-500 h-7 px-2"
                >
                  <Wifi className="w-3 h-3" />
                </ToggleGroupItem>
              </ToggleGroup>
            </div>

            <div className="h-8 w-px bg-white/5" />

            {/* Voice & Action Section */}
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className="flex flex-col items-center">
                  <Label
                    htmlFor="voice-mode"
                    className="text-[8px] font-mono uppercase tracking-widest text-zinc-600 mb-1"
                  >
                    Voice
                  </Label>
                  <Switch
                    id="voice-mode"
                    checked={isVoiceEnabled}
                    onCheckedChange={setIsVoiceEnabled}
                    className="data-[state=checked]:bg-emerald-500 h-4 w-8 scale-75"
                  />
                </div>
              </div>

              {state === "idle" ? (
                <GlowButton
                  onClick={onStart}
                  className="px-6 py-0 rounded-xl h-10 text-[10px]"
                >
                  <Play className="w-3 h-3 fill-current mr-2" />
                  Launch Agent
                </GlowButton>
              ) : (
                <button
                  onClick={onReset}
                  className="flex items-center gap-2 px-6 h-10 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors font-mono text-[10px] uppercase tracking-widest"
                >
                  <RotateCcw
                    className={cn("w-3 h-3", isRunning && "animate-spin-slow")}
                  />
                  {state === "complete" ? "Reset Link" : "Resetting..."}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Neural Waveform Overlay when running */}
        {isRunning && (
          <div className="absolute top-0 left-0 right-0 h-[2px] overflow-hidden rounded-full px-12">
            <motion.div
              animate={{ x: ["-100%", "100%"] }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              className="h-full w-1/3 bg-gradient-to-r from-transparent via-emerald-500 to-transparent"
            />
          </div>
        )}
      </div>
    </motion.div>
  );
}
