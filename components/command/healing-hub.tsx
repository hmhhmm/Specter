"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";
import { Cpu, Github, Terminal, ChevronRight, ExternalLink, Loader2 } from "lucide-react";
import { GlowButton } from "@/components/ui/glow-button";

interface HealingSuggestion {
  id: string;
  file: string;
  type: string;
  description: string;
  code_before: string;
  code_after: string;
  impact: string;
  confidence?: number;
}

export function HealingHub() {
  const [suggestion, setSuggestion] = useState<HealingSuggestion | null>(null);
  const [loading, setLoading] = useState(true);
  const [healingInProgress, setHealingInProgress] = useState(false);
  const [prUrl, setPrUrl] = useState<string | null>(null);

  useEffect(() => {
    async function fetchSuggestions() {
      try {
        const response = await fetch("http://localhost:8000/api/healing/suggestions");
        if (response.ok) {
          const data = await response.json();
          if (data.suggestions && data.suggestions.length > 0) {
            setSuggestion(data.suggestions[0]);
          } else {
            // Fallback for demo if no suggestions found
            setSuggestion({
              id: "contrast-1",
              file: "app/mock-target/page.tsx",
              type: "style",
              description: "Improve fee visibility contrast",
              code_before: ".checkout-fee { color: #0a0a0c; }",
              code_after: ".checkout-fee { color: #f4f4f5; }",
              impact: "High friction: Fee value is invisible on dark background.",
              confidence: 95
            });
          }
        }
      } catch (err) {
        console.error("Error fetching healing suggestions:", err);
        // Fallback for demo if backend is down
        setSuggestion({
          id: "contrast-1",
          file: "app/mock-target/page.tsx",
          type: "style",
          description: "Improve fee visibility contrast",
          code_before: ".checkout-fee { color: #0a0a0c; }",
          code_after: ".checkout-fee { color: #f4f4f5; }",
          impact: "High friction: Fee value is invisible on dark background.",
          confidence: 95
        });
      } finally {
        setLoading(false);
      }
    }
    fetchSuggestions();
  }, []);

  const handleOpenPR = async () => {
    if (!suggestion || !canOpenPR) return;
    
    setHealingInProgress(true);
    try {
      const response = await fetch("/api/specter-healer", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          bugId: suggestion.id,
          bugTitle: suggestion.description,
          bugDescription: suggestion.impact,
          filePath: suggestion.file,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.prUrl) {
          setPrUrl(data.prUrl);
        }
        // Update suggestion with REAL AI code if available
        if (data.codeBefore && data.codeAfter) {
          setSuggestion({
            ...suggestion,
            code_before: data.codeBefore,
            code_after: data.codeAfter,
          });
        }
      } else {
        const errorData = await response.json();
        console.error("Failed to create PR:", errorData);
        alert(`Failed to create PR: ${errorData.error || 'Unknown error'}`);
      }
    } catch (err) {
      console.error("Error creating PR:", err);
      alert('Error creating PR. Check console for details.');
    } finally {
      setHealingInProgress(false);
    }
  };

  const displayFile = suggestion?.file || "globals.css";
  const codeBefore = suggestion?.code_before || ".checkout-button {\n  color: var(--gray-mute);\n}";
  const codeAfter = suggestion?.code_after || ".checkout-button {\n  color: var(--emerald-glow);\n  box-shadow: 0 0 20px rgba(16,185,129,0.2);\n}";

  // Parse code lines for display
  const beforeLines = codeBefore.split("\n");
  const afterLines = codeAfter.split("\n");
  const confidence = suggestion?.confidence || 0;
  const canOpenPR = confidence >= 80;

  return (
    <div className="flex flex-col h-full min-h-0">
      {/* Autonomous Remediation Card - fixed height container */}
      <div className="rounded-lg bg-zinc-900/60 border border-zinc-800 p-4 flex flex-col flex-1 min-h-0 relative overflow-hidden">
        
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-zinc-800/50 border border-zinc-700 flex items-center justify-center">
              <Cpu className="w-4 h-4 text-blue-400" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">Auto-Remediation</h3>
              <p className="text-[10px] text-zinc-500 uppercase tracking-wide">System Active</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            {/* Circular Confidence Indicator */}
            <div className="relative w-12 h-12">
              <svg className="transform -rotate-90 w-12 h-12">
                <circle
                  cx="24"
                  cy="24"
                  r="20"
                  stroke="currentColor"
                  strokeWidth="3"
                  fill="none"
                  className="text-zinc-800"
                />
                <circle
                  cx="24"
                  cy="24"
                  r="20"
                  stroke="currentColor"
                  strokeWidth="3"
                  fill="none"
                  strokeDasharray={`${2 * Math.PI * 20}`}
                  strokeDashoffset={`${2 * Math.PI * 20 * (1 - confidence / 100)}`}
                  className={confidence >= 80 ? 'text-emerald-500' : 'text-amber-500'}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className={`text-[10px] font-bold ${confidence >= 80 ? 'text-emerald-400' : 'text-amber-400'}`}>
                  {confidence}%
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="mb-6 rounded-2xl bg-emerald-500/5 border border-emerald-500/10 p-4 relative group/suggestion overflow-hidden">
          <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500/40" />
          <div className="flex items-center justify-between mb-2">
            <span className="text-[9px] font-mono text-emerald-500/70 uppercase tracking-[0.2em] font-bold">Priority Diagnosis</span>
            <span className="text-[8px] font-mono text-zinc-600 bg-zinc-900/50 px-2 py-0.5 rounded-full border border-white/5">SHA-256: 8f2a...</span>
          </div>
          <p className="text-xs text-zinc-200 leading-relaxed font-medium">
            {suggestion?.description || "Analyzing codebase for potential fixes..."}
          </p>
          <p className="text-[10px] text-zinc-500 mt-2 italic">
            {suggestion?.impact || "Estimated recovery: $12,400 ARR"}
          </p>
        </div>

        {/* Primary Action Button Moved to Top */}
        <div className="mb-6">
          {prUrl ? (
            <GlowButton 
              onClick={() => prUrl !== "#" && window.open(prUrl, "_blank")}
              className="w-full py-4 text-[10px] tracking-[0.2em] uppercase flex items-center justify-center gap-3 font-bold group/btn bg-emerald-500 text-black border-none"
            >
              <Github className="w-4 h-4" />
              {prUrl === "#" ? "PR Created (Mocked)" : "View PR on GitHub"}
              <ExternalLink className="w-3 h-3 ml-1" />
            </GlowButton>
          ) : (
            <>
              <GlowButton 
                onClick={handleOpenPR}
                disabled={healingInProgress || loading || !canOpenPR}
                className="w-full py-4 text-[10px] tracking-[0.2em] uppercase flex items-center justify-center gap-3 font-bold group/btn disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {healingInProgress ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Generating Fix...
                  </>
                ) : (
                  <>
                    <Github className="w-4 h-4" />
                    Open GitHub Pull Request
                    <ChevronRight className="w-3 h-3 ml-1 group-hover/btn:translate-x-1 transition-transform" />
                  </>
                )}
              </GlowButton>
              {!canOpenPR && (
                <div className="mt-3 px-3 py-2 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-start gap-2">
                  <div className="w-4 h-4 rounded-full bg-amber-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-amber-400 text-[10px] font-bold">!</span>
                  </div>
                  <div className="flex-1">
                    <p className="text-[10px] font-medium text-amber-400 leading-relaxed">
                      Manual review required
                    </p>
                    <p className="text-[9px] text-amber-500/70 mt-0.5">
                      Confidence below threshold (80%)
                    </p>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
          <div className="flex items-center justify-between mb-4 px-1 shrink-0">
            <div className="flex items-center gap-2">
              <Terminal className="w-3 h-3 text-zinc-500" />
              <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-widest font-bold">Proposed Patch</span>
            </div>
            <span className="text-[8px] font-mono text-zinc-700 uppercase tracking-widest">{displayFile}</span>
          </div>
          
          <div className="flex-1 bg-[#080808] rounded-2xl border border-white/5 font-mono text-[10px] leading-relaxed relative overflow-hidden flex flex-col group/code min-h-0">
            <div className="absolute inset-0 opacity-[0.03] pointer-events-none bg-[url('https://grainy-gradients.vercel.app/noise.svg')]" />
            
            <div className="flex-1 min-h-0 overflow-y-auto custom-scrollbar p-5">
              <div className="mb-4 pb-2 border-b border-white/5 flex items-center justify-between sticky top-0 bg-[#080808] z-10">
                <span className="text-red-500/60 uppercase text-[8px] tracking-widest font-bold">Original State</span>
              </div>
              {beforeLines.map((line, i) => (
                <div key={`before-${i}`} className="flex gap-4 bg-red-500/5 -mx-5 px-5 py-1 border-l-2 border-red-500/50">
                  <span className="w-4 shrink-0 text-right text-red-500/40 select-none">{i + 1}</span>
                  <p className="text-red-400/90 break-all">- {line}</p>
                </div>
              ))}

              <div className="mt-8 mb-4 pb-2 border-b border-white/5 flex items-center justify-between sticky top-0 bg-[#080808] z-10">
                <span className="text-emerald-500/60 uppercase text-[8px] tracking-widest font-bold">Neural Remediation</span>
              </div>
              {afterLines.map((line, i) => (
                <div key={`after-${i}`} className="flex gap-4 bg-emerald-500/10 -mx-5 px-5 py-1 border-l-2 border-emerald-500/50 relative">
                  <span className="w-4 shrink-0 text-right text-emerald-500/40 select-none">{i + 1}</span>
                  <p className="text-emerald-500/90 break-all">+ {line}</p>
                  {i === 0 && (
                    <motion.div 
                      initial={{ x: "-100%" }}
                      animate={{ x: "100%" }}
                      transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                      className="absolute inset-0 bg-emerald-500/5 w-1/4 skew-x-12 pointer-events-none"
                    />
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-6">
          <button className="w-full py-3.5 rounded-xl border border-white/5 bg-white/5 text-[9px] font-mono text-zinc-500 uppercase tracking-widest hover:text-white hover:bg-white/10 hover:border-white/10 transition-all flex items-center justify-center gap-2 group/audit">
            <span>View Full Impact Audit</span>
            <ChevronRight className="w-3 h-3 group-hover/audit:translate-x-1 transition-transform" />
          </button>
        </div>
      </div>
    </div>
  );
}
