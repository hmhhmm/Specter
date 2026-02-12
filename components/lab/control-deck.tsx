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
      className="fixed bottom-12 left-1/2 -translate-x-1/2 z-40 w-full max-w-5xl px-6"
    >
      <div className={cn(
        "relative rounded-[2rem] border border-white/10 bg-zinc-950/80 backdrop-blur-2xl px-8 py-4 shadow-2xl transition-all duration-500 min-h-[80px] flex items-center",
        isRunning ? "border-emerald-500/30 shadow-emerald-500/10" : ""
      )}>
        <div className="flex items-center justify-between w-full gap-4">
          {/* URL Input */}
          <div className="flex items-center gap-4">
            <div className="space-y-1">
              <Label className="text-[9px] font-mono uppercase tracking-[0.2em] text-zinc-500 ml-1">Target URL</Label>
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={isRunning}
                placeholder="https://example.com"
                className="w-[280px] bg-white/5 border border-white/10 rounded-xl font-mono text-[10px] h-9 px-3 text-white placeholder:text-zinc-600 focus:outline-none focus:ring-1 focus:ring-emerald-500/50 disabled:opacity-50"
              />
            </div>
          </div>

          {/* Persona & Device Section */}
          <div className="flex items-center gap-4">
            <div className="space-y-1">
              <Label className="text-[9px] font-mono uppercase tracking-[0.2em] text-zinc-500 ml-1">Persona</Label>
              <Select value={persona} onValueChange={setPersona} disabled={isRunning}>
                <SelectTrigger className="w-[160px] bg-white/5 border-white/10 rounded-xl font-mono text-[10px] h-9">
                  <SelectValue placeholder="Select Persona" />
                </SelectTrigger>
                <SelectContent className="bg-zinc-900 border-white/10 rounded-xl">
                  <SelectItem value="zoomer" className="focus:bg-emerald-500/20 focus:text-white text-[10px]">
                    <div className="flex items-center gap-2">
                      <Zap className="w-3 h-3" />
                      <span>Zoomer (Speedster)</span>
                    </div>
                  </SelectItem>
                  <SelectItem value="boomer" className="focus:bg-emerald-500/20 focus:text-white text-[10px]">
                    <div className="flex items-center gap-2">
                      <Glasses className="w-3 h-3" />
                      <span>Boomer (The Critic)</span>
                    </div>
                  </SelectItem>
                  <SelectItem value="skeptic" className="focus:bg-emerald-500/20 focus:text-white text-[10px]">
                    <div className="flex items-center gap-2">
                      <ShieldAlert className="w-3 h-3" />
                      <span>The Skeptic</span>
                    </div>
                  </SelectItem>
                  <SelectItem value="chaos" className="focus:bg-emerald-500/20 focus:text-white text-[10px]">
                    <div className="flex items-center gap-2">
                      <Bug className="w-3 h-3" />
                      <span>Chaos Monkey</span>
                    </div>
                  </SelectItem>
                  <SelectItem value="mobile" className="focus:bg-emerald-500/20 focus:text-white text-[10px]">
                    <div className="flex items-center gap-2">
                      <Smartphone className="w-3 h-3" />
                      <span>Mobile Native</span>
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1">
              <Label className="text-[9px] font-mono uppercase tracking-[0.2em] text-zinc-500 ml-1">Device</Label>
              <Select value={device} onValueChange={setDevice} disabled={isRunning}>
                <SelectTrigger className="w-[140px] bg-white/5 border-white/10 rounded-xl font-mono text-[10px] h-9">
                  <SelectValue placeholder="Select Device" />
                </SelectTrigger>
                <SelectContent className="bg-zinc-900 border-white/10 rounded-xl">
                  <SelectItem value="iphone-15" className="focus:bg-emerald-500/20 focus:text-white text-[10px]">
                    <div className="flex items-center gap-2">
                      <Smartphone className="w-3 h-3" />
                      <span>iPhone 15 Pro</span>
                    </div>
                  </SelectItem>
                  <SelectItem value="s23" className="focus:bg-emerald-500/20 focus:text-white text-[10px]">
                    <div className="flex items-center gap-2">
                      <Smartphone className="w-3 h-3" />
                      <span>Samsung S23</span>
                    </div>
                  </SelectItem>
                  <SelectItem value="desktop" className="focus:bg-emerald-500/20 focus:text-white text-[10px]">
                    <div className="flex items-center gap-2">
                      <Monitor className="w-3 h-3" />
                      <span>Desktop Chrome</span>
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="h-8 w-px bg-white/5 mx-2" />

          {/* Network Section */}
          <div className="space-y-1">
            <Label className="text-[9px] font-mono uppercase tracking-[0.2em] text-zinc-500 ml-1">Network</Label>
            <ToggleGroup 
              type="single" 
              value={network} 
              onValueChange={(v) => v && setNetwork(v)}
              disabled={isRunning}
              className="bg-white/5 p-1 rounded-xl border border-white/10"
            >
              <ToggleGroupItem value="wifi" className="rounded-lg data-[state=on]:bg-emerald-500/20 data-[state=on]:text-emerald-500 h-7 px-3 text-[9px] font-mono">
                <Wifi className="w-3 h-3 mr-1" />
                WiFi
              </ToggleGroupItem>
              <ToggleGroupItem value="4g" className="rounded-lg data-[state=on]:bg-emerald-500/20 data-[state=on]:text-emerald-500 h-7 px-3 text-[9px] font-mono">
                <Signal className="w-3 h-3 mr-1" />
                4G
              </ToggleGroupItem>
              <ToggleGroupItem value="3g" className="rounded-lg data-[state=on]:bg-emerald-500/20 data-[state=on]:text-emerald-500 h-7 px-3 text-[9px] font-mono">
                <SignalLow className="w-3 h-3 mr-1" />
                3G
              </ToggleGroupItem>
            </ToggleGroup>
          </div>

          <div className="h-8 w-px bg-white/5 mx-2" />

          {/* Voice & Action Section */}
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
              {isVoiceEnabled ? <Volume2 className="w-3.5 h-3.5 text-emerald-500" /> : <VolumeX className="w-3.5 h-3.5 text-zinc-600" />}
              <div className="space-y-0">
                <Label htmlFor="voice-mode" className="text-[9px] font-mono uppercase tracking-widest text-zinc-500">Voice</Label>
                <Switch 
                  id="voice-mode" 
                  checked={isVoiceEnabled} 
                  onCheckedChange={setIsVoiceEnabled}
                  className="data-[state=checked]:bg-emerald-500 h-4 w-8 scale-75"
                />
              </div>
            </div>

            {state === "idle" ? (
              <GlowButton onClick={onStart} className="px-5 py-0 rounded-xl h-10 text-[10px]">
                <Play className="w-3 h-3 fill-current" />
                Start Test
              </GlowButton>
            ) : (
              <button 
                onClick={onReset}
                className="flex items-center gap-2 px-5 h-10 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors font-mono text-[10px] uppercase tracking-widest"
              >
                <RotateCcw className={cn("w-3 h-3", isRunning && "animate-spin-slow")} />
                {state === "complete" ? "Reset" : "Resetting..."}
              </button>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
