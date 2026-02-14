"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { toast } from "sonner";
import { MissionHeader } from "@/components/lab/mission-header";
import { ControlDeck } from "@/components/lab/control-deck";
import { DeviceEmulator } from "@/components/lab/device-emulator";
import { NeuralMonologue } from "@/components/lab/neural-monologue";
import { StatusBar } from "@/components/lab/status-bar";

export type SimulationState = "idle" | "scanning" | "analyzing" | "complete";

// Define the new Personas Data
const PERSONAS = [
  {
    id: 'zoomer',
    name: 'Zoomer (Speedster)',
    icon: '⚡',
    description: 'Tech-savvy Gen Z. Impatient. Skips instructions. Checks for lag.',
    color: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20 hover:bg-yellow-500/20'
  },
  {
    id: 'boomer',
    name: 'Boomer (The Critic)',
    icon: '👵',
    description: 'Anxious first-timer. Reads everything. Flags small text & confusion.',
    color: 'bg-blue-500/10 text-blue-400 border-blue-500/20 hover:bg-blue-500/20'
  },
  {
    id: 'skeptic',
    name: 'The Skeptic',
    icon: '🕵️',
    description: 'Privacy advocate. Checks Terms of Service. Avoids social logins.',
    color: 'bg-purple-500/10 text-purple-400 border-purple-500/20 hover:bg-purple-500/20'
  },
  {
    id: 'chaos',
    name: 'Chaos Monkey',
    icon: '💥',
    description: 'Clumsy user. Enters invalid data. Tries to break validation.',
    color: 'bg-red-500/10 text-red-400 border-red-500/20 hover:bg-red-500/20'
  },
  {
    id: 'mobile',
    name: 'Mobile Native',
    icon: '📱',
    description: 'Small screen user. Tests touch targets & accessibility constraints.',
    color: 'bg-green-500/10 text-green-400 border-green-500/20 hover:bg-green-500/20'
  }
];

export default function LabPage() {
  const [simulationState, setSimulationState] = useState<SimulationState>("idle");
  const [simulationStep, setSimulationStep] = useState(0);
  const [url, setUrl] = useState("https://mocked-website-wv7p.vercel.app/");
  const [persona, setPersona] = useState("zoomer");
  const [device, setDevice] = useState("iphone-15");
  const [network, setNetwork] = useState("wifi");
  const [locale, setLocale] = useState("en-US");
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(true);
  const [currentScreenshot, setCurrentScreenshot] = useState<string | null>(null);
  const [testResults, setTestResults] = useState<any>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [currentStepData, setCurrentStepData] = useState<any>(null);
  const [currentTestId, setCurrentTestId] = useState<string | null>(null);
  const [currentAction, setCurrentAction] = useState<string>("");
  const [nextTestCountdown, setNextTestCountdown] = useState<number>(0);
  
  // Live browser streaming state — live mode ON by default
  const [isLiveMode, setIsLiveMode] = useState(true);
  const [liveFrame, setLiveFrame] = useState<string | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const liveStreamRef = useRef<WebSocket | null>(null);

  // ── Refs that always point at the latest value (stale-closure safe) ──
  const isLiveModeRef = useRef(isLiveMode);
  const currentTestIdRef = useRef(currentTestId);
  useEffect(() => { isLiveModeRef.current = isLiveMode; }, [isLiveMode]);
  useEffect(() => { currentTestIdRef.current = currentTestId; }, [currentTestId]);

  const addLog = useCallback((message: string) => {
    setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${message}`]);
  }, []);

  // ── Live browser streaming functions (stable across renders) ──
  const startLiveStream = useCallback((testId: string) => {
    // Close any previous stream
    if (liveStreamRef.current) {
      try { liveStreamRef.current.close(); } catch {}
    }
    liveStreamRef.current = null;

    addLog("🎥 Connecting to live browser stream...");
    const ws = new WebSocket(`ws://localhost:8000/ws/live-stream/${testId}`);

    ws.onopen = () => {
      console.log("Live stream connected");
      addLog("Live stream active");
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.frame) {
          setLiveFrame(data.frame);
        } else if (data.error) {
          console.error("Live stream error:", data.error);
          addLog(`Live stream: ${data.error}`);
        }
      } catch {}
    };

    ws.onerror = (error) => {
      console.error("Live stream WS error", error);
      addLog("⚠️ Live stream connection failed");
      // Do NOT flip isLiveMode off — user controls the toggle
    };

    ws.onclose = () => {
      console.log("Live stream WS closed");
      // Leave liveFrame as-is so the last frame stays visible
    };

    liveStreamRef.current = ws;
  }, [addLog]);

  const stopLiveStream = useCallback(() => {
    if (liveStreamRef.current) {
      try { liveStreamRef.current.send("stop"); } catch {}
      try { liveStreamRef.current.close(); } catch {}
      liveStreamRef.current = null;
    }
    setLiveFrame(null);
  }, []);

  const handleToggleLiveMode = useCallback(() => {
    setIsLiveMode(prev => {
      if (prev) {
        // Switching to screenshot mode
        stopLiveStream();
        setLiveFrame(null);
        addLog("Switched to screenshot mode");
        return false;
      } else {
        // Switching to live mode — reconnect if test is running
        const tid = currentTestIdRef.current;
        if (tid) {
          stopLiveStream();          // tear down stale connection first
          setLiveFrame(null);        // clear old frame
          startLiveStream(tid);      // fresh connection
          addLog("Switched to live mode — connecting…");
        } else {
          addLog("Live mode enabled — will stream when test starts");
        }
        return true;
      }
    });
  }, [startLiveStream, stopLiveStream, addLog]);

  // ── Ref for message handler so the WS effect never goes stale ──
  const handleWSMessageRef = useRef<(data: any) => void>(() => {});

  // WebSocket connection (runs once; uses ref to avoid stale closure)
  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");

    ws.onopen = () => {
      console.log("WebSocket connected");
      addLog("Connected to Specter backend");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWSMessageRef.current(data);  // always calls latest handler
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      addLog("⚠️ Backend connection issue - Make sure api_server.py is running on port 8000");
    };
    ws.onclose = () => {
      console.log("WebSocket disconnected");
      addLog("⚠️ Disconnected from backend");
    };

    wsRef.current = ws;

    return () => {
      ws.close();
      if (liveStreamRef.current) liveStreamRef.current.close();
    };
  }, [addLog]);

  // ── WebSocket message handler (always fresh via ref) ──
  useEffect(() => {
    handleWSMessageRef.current = (data: any) => {
      console.log("WebSocket message received:", data.type, data);

      if (data.type === "test_started") {
        setSimulationState("scanning");
        setCurrentTestId(data.test_id);
        addLog(`Test started: ${data.test_id}`);
        toast.info("🤖 Test started", {
          description: "AI agent is now analyzing your application..."
        });

        // Start the live stream only when the user wants live mode
        if (isLiveModeRef.current) {
          startLiveStream(data.test_id);
        } else {
          addLog("Screenshot mode — live stream not started");
        }
    } else if (data.type === "step_update") {
      setSimulationState("analyzing");
      setSimulationStep(prev => prev + 1);
      const actionText = data.action || "Processing...";
      setCurrentAction(actionText);
      addLog(`Step ${data.step || simulationStep + 1}: ${actionText}`);
      
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
          analysis_complete: data.diagnosticData.analysis_complete,
          dwell_time_ms: data.diagnosticData.dwell_time_ms
        });
        
        // Add detailed diagnostic summary to terminal
        if (data.diagnosticData.diagnosis) {
          const severityBadge = data.diagnosticData.severity?.split(' - ')[0] || 'Issue';
          addLog(` ${severityBadge} - ${data.diagnosticData.responsible_team}`);
          addLog(`    ${data.diagnosticData.diagnosis}`);
          
          // Show toast for critical issues
          if (severityBadge.includes('P0') || severityBadge.includes('Critical')) {
            toast.error("🚨 Critical Issue Detected", {
              description: data.diagnosticData.diagnosis?.substring(0, 100) + "..."
            });
          } else if (severityBadge.includes('P1')) {
            toast.warning("⚠️ High Priority Issue", {
              description: data.diagnosticData.diagnosis?.substring(0, 100) + "..."
            });
          }
          
          if (data.diagnosticData.alert_sent) {
            addLog(`   Alert sent to ${data.diagnosticData.responsible_team} team`);
          }
        } else if (data.diagnosticData.ux_issues && data.diagnosticData.ux_issues.length > 0) {
          // UX issues detected - show what they are!
          addLog(`  UX Issues detected (${data.diagnosticData.ux_issues.length}):`);
          data.diagnosticData.ux_issues.forEach((issue: string, i: number) => {
            addLog(`   ${i + 1}. ${issue}`);
          });
          
          // Check if alert was sent for these UX issues
          if (data.diagnosticData.alert_sent) {
            addLog(`   Alert sent to ${data.diagnosticData.responsible_team || 'Design'} team`);
          } else {
            addLog(`   Review recommended - Alert will be sent`);
          }
        } else if (data.diagnosticData.confusion_score > 3) {
          // High confusion but no specific diagnosis
          addLog(` Elevated confusion detected (${data.diagnosticData.confusion_score}/10)`);
        } else {
          addLog(`Analysis complete - No critical issues`);
        }
      }
    } else if (data.type === "test_complete") {
      setSimulationState("complete");
      setTestResults(data.results);
      setCurrentAction("");
      addLog("Test completed");
      addLog(`Final Results: ${data.results?.passed || 0} passed, ${data.results?.failed || 0} failed`);
      
      // Start countdown for next test (5 minutes = 300 seconds)
      setNextTestCountdown(300);
      
      const failedCount = data.results?.failed || 0;
      if (failedCount > 0) {
        toast.success("✅ Test Complete", {
          description: `Found ${failedCount} issue${failedCount > 1 ? 's' : ''} that need attention`
        });
      } else {
        toast.success("✅ Test Complete", {
          description: "No critical issues detected"
        });
      }

      // Clear test ID to prevent reconnection attempts
      setCurrentTestId(null);

      // Keep the last live frame visible for 3 s, then tear down
      setTimeout(() => stopLiveStream(), 3000);
    } else if (data.type === "test_error") {
      setSimulationState("idle");
      setCurrentTestId(null);
      addLog(`Error: ${data.error}`);
      stopLiveStream();
    }
    };
  }, [addLog, startLiveStream, stopLiveStream]);

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

      // Network names now match backend directly (wifi, 4g, 3g)
      // No mapping needed

      const requestBody = {
        url: url,
        device: deviceMap[device] || "desktop",
        network: network || "wifi",
        persona: persona || "normal",
        locale: locale || "en-US",
        max_steps: 5
      };

      console.log("Starting test with config:", requestBody);

      const response = await fetch("http://localhost:8000/api/test/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody)
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
    setCurrentTestId(null);
    setCurrentAction("");
    
    // Clean up live stream (keep isLiveMode true so next test streams too)
    stopLiveStream();
    setLiveFrame(null);
  };

  return (
    <main className="relative min-h-screen bg-[#050505] text-white overflow-hidden selection:bg-emerald-500/30">
      <div className="relative z-10 flex flex-col h-screen">
        <MissionHeader 
          activePersona={persona}
          networkCondition={network}
          nextTestIn={nextTestCountdown}
        />
        
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-6 px-6 py-6 overflow-hidden pb-40">
          <DeviceEmulator 
            state={simulationState} 
            step={simulationStep} 
            device={device}
            screenshot={currentScreenshot}
            liveFrame={liveFrame}
            isLiveMode={isLiveMode}
            onToggleLiveMode={handleToggleLiveMode}
          />
          <NeuralMonologue 
            state={simulationState} 
            step={simulationStep} 
            persona={persona}
            logs={logs}
            currentStepData={currentStepData}
            results={testResults}
            currentAction={currentAction}
            maxSteps={5}
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
          locale={locale}
          setLocale={setLocale}
        />

        <StatusBar 
          state={simulationState} 
          onTerminate={handleResetSimulation}
        />
      </div>
    </main>
  );
}
