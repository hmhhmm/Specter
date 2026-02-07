"use client";

import { useState, useEffect } from "react";
import { MissionHeader } from "@/components/lab/mission-header";
import { ControlDeck } from "@/components/lab/control-deck";
import { DeviceEmulator } from "@/components/lab/device-emulator";
import { NeuralMonologue } from "@/components/lab/neural-monologue";
import { StatusBar } from "@/components/lab/status-bar";
import { motion, AnimatePresence } from "framer-motion";

export type SimulationState = "idle" | "scanning" | "analyzing" | "complete";

export default function LabPage() {
  const [simulationState, setSimulationState] = useState<SimulationState>("idle");
  const [simulationStep, setSimulationStep] = useState(0);
  const [persona, setPersona] = useState("senior");
  const [device, setDevice] = useState("iphone-15");
  const [network, setNetwork] = useState("4g");
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(true);

  // Simulation logic
  useEffect(() => {
    let timeout: NodeJS.Timeout;
    if (simulationState === "scanning") {
      timeout = setTimeout(() => {
        setSimulationState("analyzing");
        setSimulationStep(1);
      }, 3000); // 3s for scan
    } else if (simulationState === "analyzing") {
      if (simulationStep < 8) {
        timeout = setTimeout(() => {
          setSimulationStep(prev => prev + 1);
        }, 1500); // Staggered log appearance
      } else {
        setSimulationState("complete");
      }
    }
    return () => clearTimeout(timeout);
  }, [simulationState, simulationStep]);

  const handleStartSimulation = () => {
    setSimulationState("scanning");
    setSimulationStep(0);
  };

  const handleResetSimulation = () => {
    setSimulationState("idle");
    setSimulationStep(0);
  };

  return (
    <main className="relative min-h-screen bg-[#050505] text-white overflow-hidden selection:bg-emerald-500/30">
      {/* Ambient Effects */}
      <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden opacity-[0.03]">
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] brightness-100 contrast-150"></div>
      </div>
      <div className="fixed inset-0 pointer-events-none z-50 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.1)_50%),linear-gradient(90deg,rgba(255,0,0,0.03),rgba(0,255,0,0.01),rgba(0,0,255,0.03))] bg-[length:100%_4px,3px_100%] pointer-events-none opacity-20"></div>

      {/* Page Content */}
      <div className="relative z-10 flex flex-col h-screen">
        <MissionHeader />
        
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-8 px-8 py-6 overflow-hidden mb-32">
          <DeviceEmulator 
            state={simulationState} 
            step={simulationStep} 
            device={device}
          />
          <NeuralMonologue 
            state={simulationState} 
            step={simulationStep} 
            persona={persona}
          />
        </div>

        <ControlDeck 
          state={simulationState}
          onStart={handleStartSimulation}
          onReset={handleResetSimulation}
          persona={persona}
          setPersona={setPersona}
          device={device}
          setDevice={setDevice}
          network={network}
          setNetwork={setNetwork}
          isVoiceEnabled={isVoiceEnabled}
          setIsVoiceEnabled={setIsVoiceEnabled}
        />

        <StatusBar 
          state={simulationState} 
          onTerminate={handleResetSimulation}
        />
      </div>
    </main>
  );
}
