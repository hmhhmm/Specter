"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { toast } from "sonner";
import { SpecterNav } from "@/components/landing/specter-nav";
import { ControlDeck } from "@/components/lab/control-deck";
import { DeviceEmulator } from "@/components/lab/device-emulator";
import { NeuralMonologue } from "@/components/lab/neural-monologue";
import { StatusBar } from "@/components/lab/status-bar";
import { useTTS } from "@/lib/use-tts";

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
  // ── State ──
  const [simulationState, setSimulationState] = useState<SimulationState>("idle");
  const [simulationStep, setSimulationStep] = useState(0);
  const [url, setUrl] = useState("https://mocked-website-wv7p.vercel.app/");
  const [persona, setPersona] = useState("zoomer");
  const [device, setDevice] = useState("iphone-15");
  const [network, setNetwork] = useState("wifi");
  const [locale, setLocale] = useState("en-US");
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(true);
  const { speak, stop: stopTTS } = useTTS(isVoiceEnabled);
  const [currentScreenshot, setCurrentScreenshot] = useState<string | null>(null);
  const [testResults, setTestResults] = useState<any>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [currentStepData, setCurrentStepData] = useState<any>(null);
  const [currentTestId, setCurrentTestId] = useState<string | null>(null);
  const [isMounted, setIsMounted] = useState(false);
  const [currentAction, setCurrentAction] = useState<string>("");
  const [nextTestCountdown, setNextTestCountdown] = useState<number>(0);
  
  // Live browser streaming state — live mode ON by default
  const [isLiveMode, setIsLiveMode] = useState(true);
  const [liveFrame, setLiveFrame] = useState<string | null>(null);
  
  // ── Refs ──
  const wsRef = useRef<WebSocket | null>(null);
  const liveStreamRef = useRef<WebSocket | null>(null);
  const isLiveModeRef = useRef(isLiveMode);
  const currentTestIdRef = useRef(currentTestId);
  const handleWSMessageRef = useRef<(data: any) => void>(() => {});

  // Update refs to point at latest values
  useEffect(() => { isLiveModeRef.current = isLiveMode; }, [isLiveMode]);
  useEffect(() => { currentTestIdRef.current = currentTestId; }, [currentTestId]);

  // ── Utility Functions ──
  const addLog = useCallback((message: string) => {
    setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${message}`]);
  }, []);

  const startLiveStream = useCallback((testId: string) => {
    // Close any previous stream
    if (liveStreamRef.current) {
      try { liveStreamRef.current.close(); } catch {}
    }
    liveStreamRef.current = null;

    addLog("Connecting to live browser stream...");
    const ws = new WebSocket(`ws://localhost:8000/ws/live/${testId}`);
    let isConnectionActive = true;

    ws.onopen = () => {
      if (isConnectionActive) {
        console.log("Live stream connected");
        addLog("Live stream active");
      }
    };

    ws.onmessage = (event) => {
      if (!isConnectionActive) return;
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

    ws.onerror = () => {
      // Suppress errors - connection failures are expected during cleanup
    };

    ws.onclose = () => {
      if (isConnectionActive) {
        console.log("Live stream WS closed");
      }
      // Leave liveFrame as-is so the last frame stays visible
    };

    // Store both the WebSocket and a cleanup function
    const originalClose = ws.close.bind(ws);
    ws.close = function(...args) {
      isConnectionActive = false;
      return originalClose(...args);
    };

    liveStreamRef.current = ws;
  }, [addLog]);

  const stopLiveStream = useCallback(() => {
    if (liveStreamRef.current) {
      const ws = liveStreamRef.current;
      if (ws.readyState === WebSocket.OPEN) {
        try { ws.send("stop"); } catch {}
        try { ws.close(); } catch {}
      }
      liveStreamRef.current = null;
    }
    setLiveFrame(null);
  }, []);

  const handleResetSimulation = useCallback(() => {
    setSimulationState("idle");
    setSimulationStep(0);
    setLogs([]);
    setTestResults(null);
    setCurrentScreenshot(null);
    setCurrentStepData(null);
    setCurrentTestId(null);
    setCurrentAction("");
    setNextTestCountdown(0);
    
    // Clean up live stream
    stopLiveStream();
    setLiveFrame(null);

    // Stop any ongoing speech
    stopTTS();

    // Clear saved state
    localStorage.removeItem("specter_lab_state");
  }, [stopLiveStream]);

  const checkActiveTest = useCallback(async (testId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/test/${testId}`);
      if (response.ok) {
        const data = await response.json();
        if (data.status === "running") {
          addLog(`Reattaching to active test: ${testId}`);
          if (isLiveModeRef.current) {
            startLiveStream(testId);
          }
        } else if (data.status === "completed") {
          setSimulationState("complete");
          setTestResults(data.result);
          addLog("Test was completed while you were away.");
        }
      } else {
        // Test no longer exists or server restarted
        handleResetSimulation();
      }
    } catch (e) {
      console.error("Failed to check active test", e);
    }
  }, [addLog, startLiveStream, handleResetSimulation]);

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

  // ── Persistence Effects ──
  
  // Save state to localStorage
  useEffect(() => {
    if (!isMounted) return;
    const state = {
      simulationState,
      simulationStep,
      url,
      persona,
      device,
      network,
      logs,
      currentTestId,
      currentStepData,
      testResults
    };
    localStorage.setItem("specter_lab_state", JSON.stringify(state));
  }, [simulationState, simulationStep, url, persona, device, network, logs, currentTestId, currentStepData, testResults, isMounted]);

  // Load state from localStorage on mount
  useEffect(() => {
    const savedState = localStorage.getItem("specter_lab_state");
    if (savedState) {
      try {
        const parsed = JSON.parse(savedState);
        setSimulationState(parsed.simulationState || "idle");
        setSimulationStep(parsed.simulationStep || 0);
        setUrl(parsed.url || "https://mocked-website-wv7p.vercel.app/");
        setPersona(parsed.persona || "zoomer");
        setDevice(parsed.device || "iphone-15");
        setNetwork(parsed.network || "wifi");
        setLogs(parsed.logs || []);
        setCurrentTestId(parsed.currentTestId || null);
        setCurrentStepData(parsed.currentStepData || null);
        setTestResults(parsed.testResults || null);
        
        // If there's an active test, check if it's still running
        if (parsed.currentTestId && (parsed.simulationState === "scanning" || parsed.simulationState === "analyzing")) {
          checkActiveTest(parsed.currentTestId);
        }
      } catch (e) {
        console.error("Failed to load saved state", e);
      }
    }
    setIsMounted(true);
  }, [checkActiveTest]);

  // ── WebSocket Connection Effect ──
  useEffect(() => {
    let isActive = true;
    const ws = new WebSocket("ws://localhost:8000/ws");

    ws.onopen = () => {
      if (isActive) {
        console.log("WebSocket connected");
        addLog("Connected to Specter backend");
      }
    };

    ws.onmessage = (event) => {
      if (!isActive) return;
      const data = JSON.parse(event.data);
      handleWSMessageRef.current(data);  // always calls latest handler
    };

    ws.onerror = () => {
      // Suppress errors during cleanup or React strict mode
    };
    
    ws.onclose = (event) => {
      // Only log if this was an unexpected disconnect while active
      if (isActive && event.code !== 1000 && event.code !== 1001) {
        console.log("WebSocket disconnected unexpectedly", event.code);
        addLog("⚠️ Backend connection interrupted");
      }
    };

    wsRef.current = ws;

    return () => {
      isActive = false;
      ws.close();
      if (liveStreamRef.current) liveStreamRef.current.close();
    };
  }, [addLog]);

  // ── WebSocket Message Handler Effect ──
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
            alert_sent: data.stepData.alert_sent,
            observation: data.stepData.observation,
            reasoning: data.stepData.reasoning
          });

          // NOTE: observation and reasoning are NOT available here yet —
          // screenshot_callback fires BEFORE the LLM returns its plan.
          // They are logged in the diagnostic_update handler below.
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
            dwell_time_ms: data.diagnosticData.dwell_time_ms,
            observation: data.diagnosticData.observation,
            reasoning: data.diagnosticData.reasoning
          });
          
          // Narrate diagnosis if present (vision and reasoning are NOT narrated to reduce lag)
          if (data.diagnosticData.diagnosis) {
            speak(data.diagnosticData.diagnosis);
          }
          
          // Log Vision and Thought FIRST (before diagnosis) — natural order
          // These are only available in diagnostic_update, NOT in step_update
          if (data.diagnosticData.observation) {
            addLog(`Vision: ${data.diagnosticData.observation}`);
          }
          if (data.diagnosticData.reasoning) {
            addLog(`Thought: ${data.diagnosticData.reasoning}`);
          }
          
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
            if (data.diagnosticData.alert_sent) {
              addLog(`   Alert sent to ${data.diagnosticData.responsible_team || 'Design'} team`);
            }
          }
        }
      } else if (data.type === "test_complete") {
        setSimulationState("complete");
        setTestResults(data.results);
        setCurrentAction("");
        addLog("Test completed");
        addLog(`Final Results: ${data.results?.passed || 0} passed, ${data.results?.failed || 0} failed`);
        
        // Narrate completion if there's a reason
        if (data.results?.reason) {
          speak(data.results.reason);
        } else {
          speak(`Test complete. ${data.results?.passed || 0} steps passed, ${data.results?.failed || 0} issues detected.`);
        }

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
  }, [addLog, startLiveStream, stopLiveStream, simulationStep]);

  // ── Event Handlers ──
  const handleStartSimulation = async () => {
    setSimulationState("scanning");
    setSimulationStep(0);
    setLogs([]);
    setTestResults(null);
    addLog("Starting autonomous test...");

    try {
      const deviceMap: Record<string, string> = {
        "iphone-15": "iphone13",
        "s23": "android",
        "macbook": "desktop"
      };

      const requestBody = {
        url: url,
        device: deviceMap[device] || "desktop",
        network: network || "wifi",
        persona: persona || "normal",
        locale: locale || "en-US",
        max_steps: 20
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

  return (
    <main className="relative min-h-screen bg-white dark:bg-[#050505] text-zinc-900 dark:text-white overflow-hidden selection:bg-emerald-500/30 transition-colors duration-300">
      <div className="relative z-10 flex flex-col h-screen">
        <SpecterNav />
        
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-8 px-8 py-6 overflow-hidden mb-32 mt-28">
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
            maxSteps={20}
            isVoiceEnabled={isVoiceEnabled}
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
