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
    <div className="fixed bottom-10 left-1/2 -translate-x-1/2 z-40 w-full max-w-6xl px-6">
      <div className={cn(
        "relative rounded-2xl border border-white/10 bg-zinc-950/90 backdrop-blur-xl px-6 py-4 shadow-2xl transition-all duration-500",
        isRunning ? "border-emerald-500/30 shadow-emerald-500/10" : ""
      )}>
        {/* Main Controls Grid */}
        <div className="grid grid-cols-[300px_auto_1fr_auto] gap-6 items-end">
          {/* URL Input */}
          <div className="space-y-1.5">
            <Label className="text-[8px] font-mono uppercase tracking-wider text-zinc-500">Target URL</Label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={isRunning}
              placeholder="https://example.com"
              className="w-full bg-white/5 border border-white/10 rounded-lg font-mono text-xs h-9 px-3 text-white placeholder:text-zinc-600 focus:outline-none focus:ring-1 focus:ring-emerald-500/50 disabled:opacity-50 transition-all"
            />
          </div>

          {/* Persona & Device */}
          <div className="flex gap-3">
            <div className="space-y-1.5">
              <Label className="text-[8px] font-mono uppercase tracking-wider text-zinc-500">Persona</Label>
              <Select value={persona} onValueChange={setPersona} disabled={isRunning}>
                <SelectTrigger className="w-[170px] bg-white/5 border-white/10 rounded-lg font-mono text-xs h-9">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-zinc-900 border-white/10 rounded-lg">
                  <SelectItem value="elderly" className="focus:bg-emerald-500/20 text-xs">
                    <div className="flex items-center gap-2">
                      <User className="w-3 h-3" />
                      <span>Elderly User</span>
                    </div>
                  </SelectItem>
                  <SelectItem value="normal" className="focus:bg-emerald-500/20 text-xs">
                    <div className="flex items-center gap-2">
                      <Briefcase className="w-3 h-3" />
                      <span>Normal User</span>
                    </div>
                  </SelectItem>
                  <SelectItem value="cautious" className="focus:bg-emerald-500/20 text-xs">
                    <div className="flex items-center gap-2">
                      <ShoppingCart className="w-3 h-3" />
                      <span>Cautious User</span>
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1.5">
              <Label className="text-[8px] font-mono uppercase tracking-wider text-zinc-500">Device</Label>
              <Select value={device} onValueChange={setDevice} disabled={isRunning}>
                <SelectTrigger className="w-[150px] bg-white/5 border-white/10 rounded-lg font-mono text-xs h-9">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-zinc-900 border-white/10 rounded-lg">
                  <SelectItem value="iphone-15" className="focus:bg-emerald-500/20 text-xs">
                    <div className="flex items-center gap-2">
                      <Smartphone className="w-3 h-3" />
                      <span>iPhone 15 Pro</span>
                    </div>
                  </SelectItem>
                  <SelectItem value="s23" className="focus:bg-emerald-500/20 text-xs">
                    <div className="flex items-center gap-2">
                      <Smartphone className="w-3 h-3" />
                      <span>Samsung S23</span>
                    </div>
                  </SelectItem>
                  <SelectItem value="desktop" className="focus:bg-emerald-500/20 text-xs">
                    <div className="flex items-center gap-2">
                      <Monitor className="w-3 h-3" />
                      <span>Desktop</span>
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Network & Voice */}
          <div className="flex items-end gap-4">
            <div className="space-y-1.5">
              <Label className="text-[8px] font-mono uppercase tracking-wider text-zinc-500">Network</Label>
              <ToggleGroup 
                type="single" 
                value={network} 
                onValueChange={(v) => v && setNetwork(v)}
                disabled={isRunning}
                className="bg-white/5 p-1 rounded-lg border border-white/10"
              >
                <ToggleGroupItem value="5g" className="rounded data-[state=on]:bg-emerald-500/20 data-[state=on]:text-emerald-500 h-7 px-3">
                  <Signal className="w-3.5 h-3.5" />
                </ToggleGroupItem>
                <ToggleGroupItem value="4g" className="rounded data-[state=on]:bg-emerald-500/20 data-[state=on]:text-emerald-500 h-7 px-3">
                  <SignalLow className="w-3.5 h-3.5" />
                </ToggleGroupItem>
                <ToggleGroupItem value="3g" className="rounded data-[state=on]:bg-emerald-500/20 data-[state=on]:text-emerald-500 h-7 px-3">
                  <Wifi className="w-3.5 h-3.5" />
                </ToggleGroupItem>
              </ToggleGroup>
            </div>

            <div className="flex items-center gap-2 h-9">
              {isVoiceEnabled ? <Volume2 className="w-4 h-4 text-emerald-500" /> : <VolumeX className="w-4 h-4 text-zinc-600" />}
              <div className="flex flex-col gap-0.5">
                <Label htmlFor="voice-mode" className="text-[8px] font-mono uppercase tracking-wider text-zinc-500 leading-none">Voice</Label>
                <Switch 
                  id="voice-mode" 
                  checked={isVoiceEnabled} 
                  onCheckedChange={setIsVoiceEnabled}
                  className="data-[state=checked]:bg-emerald-500"
                />
              </div>
            </div>
          </div>

          {/* Action Button */}
          <div>
            {state === "idle" ? (
              <GlowButton onClick={onStart} className="px-6 h-9 rounded-lg text-xs">
                <Play className="w-3.5 h-3.5 fill-current" />
                Launch Agent
              </GlowButton>
            ) : (
              <button 
                onClick={onReset}
                className="flex items-center gap-2 px-6 h-9 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors font-mono text-xs uppercase tracking-wider"
              >
                <RotateCcw className={cn("w-3.5 h-3.5", isRunning && "animate-spin-slow")} />
                {state === "complete" ? "Reset" : "Resetting..."}
              </button>
            )}
          </div>
        </div>

        {/* Progress indicator when running */}
        {isRunning && (
          <div className="absolute top-0 left-0 right-0 h-[2px] overflow-hidden rounded-t-2xl">
            <div className="h-full w-full bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent animate-pulse" />
          </div>
        )}
      </div>
    </div>
  );
}
