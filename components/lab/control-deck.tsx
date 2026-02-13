"use client";

import { motion } from "framer-motion";
import { 
  Zap, 
  Glasses, 
  ShieldAlert, 
  Bug, 
  Smartphone, 
  Monitor, 
  Signal, 
  SignalLow, 
  Wifi, 
  Volume2, 
  VolumeX,
  Play,
  RotateCcw
} from "lucide-react";
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
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
  url: string;
  setUrl: (v: string) => void;
  persona: string;
  setPersona: (v: string) => void;
  device: string;
  setDevice: (v: string) => void;
  network: string;
  setNetwork: (v: string) => void;
  isVoiceEnabled: boolean;
  setIsVoiceEnabled: (v: boolean) => void;
}

export function ControlDeck({
  state,
  onStart,
  onReset,
  url,
  setUrl,
  persona,
  setPersona,
  device,
  setDevice,
  network,
  setNetwork,
  isVoiceEnabled,
  setIsVoiceEnabled
}: ControlDeckProps) {
  const isRunning = state !== "idle" && state !== "complete";

  return (
    <motion.div 
      initial={{ y: 100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: 0.5, duration: 0.8 }}
      className="fixed bottom-16 left-1/2 -translate-x-1/2 z-40 w-full max-w-6xl px-4"
    >
      <div className={cn(
        "relative rounded-xl border border-white/10 bg-zinc-950/95 backdrop-blur-xl px-4 py-3 shadow-2xl transition-all duration-500",
        isRunning ? "border-emerald-500/30 shadow-emerald-500/10" : ""
      )}>
        <div className="flex items-center justify-between w-full gap-3">
          {/* URL Input */}
          <div className="flex-shrink min-w-0">
            <Label className="text-[8px] font-mono uppercase tracking-wider text-zinc-500 mb-1 block">Target URL</Label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={isRunning}
              placeholder="https://example.com"
              className="w-[240px] bg-white/5 border border-white/10 rounded-lg font-mono text-[10px] h-8 px-2.5 text-white placeholder:text-zinc-600 focus:outline-none focus:ring-1 focus:ring-emerald-500/50 disabled:opacity-50"
            />
          </div>

          {/* Persona */}
          <div className="flex-shrink-0">
            <Label className="text-[8px] font-mono uppercase tracking-wider text-zinc-500 mb-1 block">Persona</Label>
            <Select value={persona} onValueChange={setPersona} disabled={isRunning}>
              <SelectTrigger className="w-[140px] bg-white/5 border-white/10 rounded-lg font-mono text-[10px] h-8">
                <SelectValue placeholder="Select" />
              </SelectTrigger>
              <SelectContent className="bg-zinc-900 border-white/10 rounded-lg">
                <SelectItem value="zoomer" className="text-[10px]">⚡ Zoomer</SelectItem>
                <SelectItem value="boomer" className="text-[10px]">👵 Boomer</SelectItem>
                <SelectItem value="skeptic" className="text-[10px]">🕵️ Skeptic</SelectItem>
                <SelectItem value="chaos" className="text-[10px]">💥 Chaos</SelectItem>
                <SelectItem value="mobile" className="text-[10px]">📱 Mobile</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Device */}
          <div className="flex-shrink-0">
            <Label className="text-[8px] font-mono uppercase tracking-wider text-zinc-500 mb-1 block">Device</Label>
            <Select value={device} onValueChange={setDevice} disabled={isRunning}>
              <SelectTrigger className="w-[120px] bg-white/5 border-white/10 rounded-lg font-mono text-[10px] h-8">
                <SelectValue placeholder="Select" />
              </SelectTrigger>
              <SelectContent className="bg-zinc-900 border-white/10 rounded-lg">
                <SelectItem value="iphone-15" className="text-[10px]">iPhone 15 P</SelectItem>
                <SelectItem value="s23" className="text-[10px]">Samsung S23</SelectItem>
                <SelectItem value="desktop" className="text-[10px]">Desktop</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Network */}
          <div className="flex-shrink-0">
            <Label className="text-[8px] font-mono uppercase tracking-wider text-zinc-500 mb-1 block">Network</Label>
            <ToggleGroup 
              type="single" 
              value={network} 
              onValueChange={(v) => v && setNetwork(v)}
              disabled={isRunning}
              className="bg-white/5 p-0.5 rounded-lg border border-white/10"
            >
              <ToggleGroupItem value="wifi" className="rounded data-[state=on]:bg-emerald-500/20 data-[state=on]:text-emerald-500 h-7 px-2.5 text-[9px] font-mono">
                <Wifi className="w-3 h-3" />
              </ToggleGroupItem>
              <ToggleGroupItem value="4g" className="rounded data-[state=on]:bg-emerald-500/20 data-[state=on]:text-emerald-500 h-7 px-2.5 text-[9px] font-mono">
                4G
              </ToggleGroupItem>
              <ToggleGroupItem value="3g" className="rounded data-[state=on]:bg-emerald-500/20 data-[state=on]:text-emerald-500 h-7 px-2.5 text-[9px] font-mono">
                3G
              </ToggleGroupItem>
            </ToggleGroup>
          </div>

          {/* Voice */}
          <div className="flex-shrink-0 flex items-end gap-2 pb-0.5">
            <Label className="text-[8px] font-mono uppercase tracking-wider text-zinc-500">Voice</Label>
            <Switch 
              id="voice-mode" 
              checked={isVoiceEnabled} 
              onCheckedChange={setIsVoiceEnabled}
              className="data-[state=checked]:bg-emerald-500 h-4 w-7"
            />
          </div>

          {/* Action Button */}
          <div className="flex-shrink-0">
            {state === "idle" ? (
              <GlowButton onClick={onStart} className="px-4 py-0 rounded-lg h-8 text-[10px] mt-auto">
                <Play className="w-3 h-3 fill-current" />
                Start Test
              </GlowButton>
            ) : (
              <button 
                onClick={onReset}
                className="flex items-center gap-2 px-4 h-8 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors font-mono text-[10px] uppercase"
              >
                <RotateCcw className={cn("w-3 h-3", isRunning && "animate-spin-slow")} />
                {state === "complete" ? "Reset" : "..."}
              </button>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
