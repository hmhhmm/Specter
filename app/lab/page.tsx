"use client";

import { useState, useEffect, useRef } from "react";
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
  const [url, setUrl] = useState("https://deriv.com/signup");
  const [persona, setPersona] = useState("senior");
  const [device, setDevice] = useState("iphone-15");
  const [network, setNetwork] = useState("4g");
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(true);
  const [currentScreenshot, setCurrentScreenshot] = useState<string | null>(null);
  const [testResults, setTestResults] = useState<any>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [currentStepData, setCurrentStepData] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // WebSocket connection
  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");
    
    ws.onopen = () => {
      console.log("WebSocket connected");
      addLog("Connected to Specter backend");
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };
    
    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };
    
    ws.onclose = () => {
      console.log("WebSocket disconnected");
    };
    
    wsRef.current = ws;
    
    return () => {
      ws.close();
    };
  }, []);

  const addLog = (message: string) => {
    setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${message}`]);
  };

  const handleWebSocketMessage = (data: any) => {
    console.log("WebSocket message received:", data.type, data);
    
    if (data.type === "test_started") {
      setSimulationState("scanning");
      addLog(`Test started: ${data.test_id}`);
    } else if (data.type === "step_update") {
      setSimulationState("analyzing");
      setSimulationStep(prev => prev + 1);
      addLog(`Step ${data.step || simulationStep + 1}: ${data.action || "Processing..."}`);
      
      // Update current step diagnostic data (if available immediately)
      if (data.stepData) {
        setCurrentStepData({
          confusion_score: data.stepData.confusion_score,
          network_logs: data.stepData.network_logs,
          f_score: data.stepData.f_score,
          diagnosis: data.stepData.diagnosis,
          severity: data.stepData.severity,
          responsible_team: data.stepData.responsible_team,
          ux_issues: data.stepData.ux_issues,
          alert_sent: data.stepData.alert_sent
        });
      }
      
      if (data.screenshot) {
        console.log("Setting screenshot, length:", data.screenshot.length);
        setCurrentScreenshot(data.screenshot);
      } else {
        console.log("No screenshot in message");
      }
    } else if (data.type === "diagnostic_update") {
      // Separate diagnostic data broadcast after step analysis completes
      if (data.diagnosticData) {
        setCurrentStepData({
          confusion_score: data.diagnosticData.confusion_score,
          network_logs: data.diagnosticData.network_logs,
          console_logs: data.diagnosticData.console_logs,
          f_score: data.diagnosticData.f_score,
          diagnosis: data.diagnosticData.diagnosis,
          severity: data.diagnosticData.severity,
          responsible_team: data.diagnosticData.responsible_team,
          ux_issues: data.diagnosticData.ux_issues,
          alert_sent: data.diagnosticData.alert_sent,
          dwell_time_ms: data.diagnosticData.dwell_time_ms
        });
        
        // Add concise diagnostic summary to terminal
        if (data.diagnosticData.diagnosis) {
          addLog(`🔍 ${data.diagnosticData.severity || 'Issue'} - ${data.diagnosticData.responsible_team}`);
          if (data.diagnosticData.alert_sent) {
            addLog(`   🚨 Alert sent to ${data.diagnosticData.responsible_team} team`);
          }
        } else if (data.diagnosticData.ux_issues && data.diagnosticData.ux_issues.length > 0) {
          // UX issues detected but not critical enough for alarm
          addLog(`⚠️  UX Issues detected (${data.diagnosticData.ux_issues.length}) - Review recommended`);
        } else if (data.diagnosticData.confusion_score > 3) {
          // High confusion but no specific diagnosis
          addLog(`⚠️  Elevated confusion detected (${data.diagnosticData.confusion_score}/10)`);
        } else {
          addLog(`✓ Analysis complete - No critical issues`);
        }
      }
    } else if (data.type === "test_complete") {
      setSimulationState("complete");
      setTestResults(data.results);
      addLog("Test completed");
      addLog(`Final Results: ${data.results?.passed || 0} passed, ${data.results?.failed || 0} failed`);
    } else if (data.type === "test_error") {
      setSimulationState("idle");
      addLog(`Error: ${data.error}`);
    }
  };

  const handleStartSimulation = async () => {
    setSimulationState("scanning");
    setSimulationStep(0);
    setLogs([]);
    setTestResults(null);
    addLog("Starting autonomous test...");

    try {
      // Map UI device names to backend device names
      const deviceMap: Record<string, string> = {
        "iphone-15": "iphone13",
        "s23": "android",
        "macbook": "desktop"
      };

      // Map UI network names to backend network names
      const networkMap: Record<string, string> = {
        "5g": "wifi",
        "4g": "4g",
        "3g": "3g"
      };

      // Map UI persona names to backend persona names  
      const personaMap: Record<string, string> = {
        "senior": "elderly",
        "pro": "cautious",
        "casual": "normal"
      };

      const response = await fetch("http://localhost:8000/api/test/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          url: url,
          device: deviceMap[device] || "desktop",
          network: networkMap[network] || "wifi",
          persona: personaMap[persona] || "normal",
          max_steps: 15
        })
      });

      if (!response.ok) {
        throw new Error("Failed to start test");
      }

      const data = await response.json();
      addLog(`Test ID: ${data.test_id}`);
    } catch (error: any) {
      addLog(`Error: ${error.message}`);
      setSimulationState("idle");
    }
  };

  const handleResetSimulation = () => {
    setSimulationState("idle");
    setSimulationStep(0);
    setLogs([]);
    setTestResults(null);
    setCurrentScreenshot(null);
    setCurrentStepData(null);
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
            screenshot={currentScreenshot}
          />
          <NeuralMonologue 
            state={simulationState} 
            step={simulationStep} 
            persona={persona}
            logs={logs}
            currentStepData={currentStepData}
            results={testResults}
          />
        </div>

        <ControlDeck 
          state={simulationState}
          onStart={handleStartSimulation}
          onReset={handleResetSimulation}
          url={url}
          setUrl={setUrl}
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
