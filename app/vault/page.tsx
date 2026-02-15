"use client";

import { useState, useEffect } from "react";
import { SpecterNav } from "@/components/landing/specter-nav";
import { StatusBar } from "@/components/lab/status-bar";
import { RunCard } from "@/components/vault/run-card";
import { Search, Filter } from "lucide-react";
import { cn } from "@/lib/utils";

export default function VaultPage() {
  const [runs, setRuns] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedRuns, setExpandedRuns] = useState<Set<string>>(new Set());
  const [searchQuery, setSearchQuery] = useState("");

  // Fetch test runs from backend
  useEffect(() => {
    let isActive = true;
    
    const fetchRuns = async () => {
      try {
        setIsLoading(true);
        const response = await fetch("http://localhost:8000/api/reports/list");
        
        if (!response.ok) {
          throw new Error(`Failed to fetch test runs: ${response.status}`);
        }
        
        const data = await response.json();
        if (isActive) {
          setRuns(data.reports || []);
          setError(null);
        }
      } catch (err: any) {
        if (isActive) {
          console.error("Error fetching test runs:", err);
          setError(err.message || "Failed to load test runs");
        }
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    };

    fetchRuns();
    
    // Connect to WebSocket for real-time updates
    const ws = new WebSocket("ws://localhost:8000/ws");
    
    ws.onopen = () => {
      if (isActive) {
        console.log("Vault: Connected to backend for real-time updates");
      }
    };
    
    ws.onmessage = (event) => {
      if (!isActive) return;
      try {
        const data = JSON.parse(event.data);
        
        // Refresh runs when test completes
        if (data.type === "test_complete") {
          fetchRuns();
        }
      } catch (error) {
        // Ignore parsing errors
      }
    };
    
    ws.onerror = () => {
      // Suppress errors
    };
    
    ws.onclose = () => {
      // Silent cleanup
    };
    
    // Poll for updates every 30 seconds as backup
    const interval = setInterval(() => {
      if (isActive) fetchRuns();
    }, 30000);
    
    return () => {
      isActive = false;
      clearInterval(interval);
      ws.close();
    };
  }, []);

  const handleToggleRun = (runId: string) => {
    setExpandedRuns(prev => {
      const newSet = new Set(prev);
      if (newSet.has(runId)) {
        newSet.delete(runId);
      } else {
        newSet.add(runId);
      }
      return newSet;
    });
  };

  // Filter runs by search query
  const filteredRuns = runs.filter((run: any) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return run.id.toLowerCase().includes(query);
  });

  // Calculate summary stats
  const totalTests = runs.reduce((sum: number, run: any) => sum + (run.step_count || 0), 0);
  const totalPass = runs.reduce((sum: number, run: any) => sum + Math.max(0, (run.step_count || 0) - (run.incident_count || 0)), 0);
  const totalFail = runs.reduce((sum: number, run: any) => sum + (run.incident_count || 0), 0);
  const avgFriction = runs.length > 0 
    ? runs.reduce((sum: number, run: any) => sum + (run.avg_f_score || 0), 0) / runs.length 
    : 0;
  const totalIssues = runs.reduce((sum: number, run: any) => {
    const breakdown = run.severity_breakdown || {};
    return sum + (breakdown.P0 || 0) + (breakdown.P1 || 0) + (breakdown.P2 || 0) + (breakdown.P3 || 0);
  }, 0);
  const criticalIssues = runs.reduce((sum: number, run: any) => sum + (run.severity_breakdown?.P0 || 0), 0);
  const highIssues = runs.reduce((sum: number, run: any) => sum + (run.severity_breakdown?.P1 || 0), 0);
  const mediumIssues = runs.reduce((sum: number, run: any) => sum + (run.severity_breakdown?.P2 || 0), 0);
  
  const readinessScore = totalTests > 0 ? Math.round(((totalPass / totalTests) * 100)) : 0;

  return (
    <main className="relative min-h-screen bg-white dark:bg-[#050505] text-zinc-900 dark:text-white overflow-hidden selection:bg-emerald-500/30 transition-colors duration-300">
      {/* Grain overlay */}
      <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden opacity-[0.02] dark:opacity-[0.03]">
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] brightness-100 contrast-150"></div>
      </div>

      {/* Scanline effect */}
      <div className="fixed inset-0 pointer-events-none z-50 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.1)_50%)] bg-[length:100%_4px] opacity-5 dark:opacity-20"></div>

      {/* Background grid */}
      <div className="fixed inset-0 z-0 opacity-[0.03] dark:opacity-10 pointer-events-none">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:40px_40px]"></div>
      </div>

      {/* Page Content */}
      <div className="relative z-10 flex flex-col min-h-screen">
        <SpecterNav />

        <div className="flex-1 px-8 py-12 max-w-7xl mx-auto w-full mb-20 mt-20">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-3">
              <h1 className="text-5xl font-bold bg-gradient-to-r from-zinc-900 to-zinc-600 dark:from-white dark:to-zinc-400 bg-clip-text text-transparent transition-colors duration-300">
                Evidence Vault
              </h1>
              {runs.length > 0 && (
                <div className="px-3 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 text-sm font-semibold transition-colors duration-300">
                  {runs.length} Run{runs.length !== 1 ? 's' : ''}
                </div>
              )}
            </div>
            <p className="text-zinc-600 dark:text-zinc-500 text-base transition-colors duration-300">
              Complete QA test history with forensic evidence and diagnostic reports
            </p>
          </div>

          {/* Summary Stats Dashboard */}
          {runs.length > 0 && (
            <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
              {/* Readiness Score */}
              <div className="col-span-1 rounded-xl bg-gradient-to-br from-emerald-50 to-white dark:from-emerald-500/10 dark:to-emerald-500/5 border-2 border-emerald-400/40 dark:border-emerald-500/20 p-4 shadow-sm transition-colors duration-300">
                <div className="text-xs text-emerald-600 dark:text-emerald-400 font-semibold mb-1 transition-colors duration-300">Readiness Score</div>
                <div className="text-3xl font-bold text-zinc-900 dark:text-white mb-2 transition-colors duration-300">{readinessScore}%</div>
                <div className="w-full h-2 rounded-full bg-zinc-200 dark:bg-white/10 overflow-hidden transition-colors duration-300">
                  <div 
                    className="h-full bg-gradient-to-r from-emerald-500 to-emerald-400 rounded-full transition-all"
                    style={{ width: `${readinessScore}%` }}
                  />
                </div>
              </div>

              {/* Tests Completed */}
              <div className="rounded-xl bg-white dark:bg-white/5 border-2 border-zinc-300 dark:border-white/10 p-4 shadow-sm transition-colors duration-300">
                <div className="text-xs text-zinc-600 dark:text-zinc-500 mb-1 transition-colors duration-300">Tests Completed</div>
                <div className="text-3xl font-bold text-zinc-900 dark:text-white transition-colors duration-300">{totalTests}</div>
                <div className="text-xs text-zinc-500 dark:text-zinc-600 mt-1 transition-colors duration-300">{runs.length} run{runs.length !== 1 ? 's' : ''}</div>
              </div>

              {/* Pass */}
              <div className="rounded-xl bg-white dark:bg-white/5 border-2 border-zinc-300 dark:border-white/10 p-4 shadow-sm transition-colors duration-300">
                <div className="text-xs text-zinc-600 dark:text-zinc-500 mb-1 transition-colors duration-300">Pass</div>
                <div className="text-3xl font-bold text-emerald-600 dark:text-emerald-400 transition-colors duration-300">{totalPass}</div>
                <div className="text-xs text-emerald-700 dark:text-emerald-600 mt-1 transition-colors duration-300">
                  {totalTests > 0 ? Math.round((totalPass/totalTests)*100) : 0}% success
                </div>
              </div>

              {/* Fail */}
              <div className="rounded-xl bg-white dark:bg-white/5 border-2 border-zinc-300 dark:border-white/10 p-4 shadow-sm transition-colors duration-300">
                <div className="text-xs text-zinc-600 dark:text-zinc-500 mb-1 transition-colors duration-300">Fail</div>
                <div className="text-3xl font-bold text-red-600 dark:text-red-400 transition-colors duration-300">{totalFail}</div>
                <div className="text-xs text-red-700 dark:text-red-600 mt-1 transition-colors duration-300">{criticalIssues} critical</div>
              </div>

              {/* Avg Friction */}
              <div className="rounded-xl bg-white dark:bg-white/5 border-2 border-zinc-300 dark:border-white/10 p-4 shadow-sm transition-colors duration-300">
                <div className="text-xs text-zinc-600 dark:text-zinc-500 mb-1 transition-colors duration-300">Avg Friction</div>
                <div className={cn(
                  "text-3xl font-bold",
                  avgFriction >= 60 ? "text-red-400" : avgFriction >= 40 ? "text-orange-400" : "text-emerald-400"
                )}>
                  {avgFriction.toFixed(0)}
                </div>
                <div className="text-xs text-zinc-500 dark:text-zinc-600 mt-1 transition-colors duration-300">out of 100</div>
              </div>
            </div>
          )}

          {/* Issue Distribution */}
          {runs.length > 0 && totalIssues > 0 && (
            <div className="rounded-xl bg-white dark:bg-white/5 border-2 border-zinc-300 dark:border-white/10 p-6 mb-8 shadow-sm transition-colors duration-300">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-zinc-900 dark:text-white transition-colors duration-300">Issue Distribution</h3>
                <div className="text-2xl font-bold text-zinc-900 dark:text-white transition-colors duration-300">{totalIssues}</div>
              </div>
              <div className="flex items-center gap-3">
                {criticalIssues > 0 && (
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-500/10 border border-red-500/30">
                      <div className="w-2 h-2 rounded-full bg-red-500" />
                      <span className="text-sm text-red-400 font-semibold">{criticalIssues}</span>
                    </div>
                    <span className="text-xs text-zinc-600 dark:text-zinc-500 transition-colors duration-300">Critical</span>
                  </div>
                )}
                {highIssues > 0 && (
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-orange-500/10 border border-orange-500/30">
                      <div className="w-2 h-2 rounded-full bg-orange-500" />
                      <span className="text-sm text-orange-400 font-semibold">{highIssues}</span>
                    </div>
                    <span className="text-xs text-zinc-600 dark:text-zinc-500 transition-colors duration-300">High</span>
                  </div>
                )}
                {mediumIssues > 0 && (
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
                      <div className="w-2 h-2 rounded-full bg-yellow-500" />
                      <span className="text-sm text-yellow-400 font-semibold">{mediumIssues}</span>
                    </div>
                    <span className="text-xs text-zinc-600 dark:text-zinc-500 transition-colors duration-300">Medium</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Search Bar */}
          <div className="mb-6">
            <div className="relative max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-600 dark:text-zinc-500 transition-colors duration-300" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search runs..."
                className="w-full pl-10 pr-4 py-2.5 bg-zinc-100 dark:bg-white/5 border border-zinc-300 dark:border-white/10 rounded-lg text-sm text-zinc-900 dark:text-white placeholder:text-zinc-500 dark:placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-colors duration-300"
              />
            </div>
          </div>

          {/* Loading State */}
          {isLoading && runs.length === 0 ? (
            <div className="text-center py-20">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-emerald-500 border-t-transparent"></div>
              <p className="mt-4 text-zinc-600 dark:text-zinc-400 transition-colors duration-300">Loading test runs...</p>
            </div>
          ) : error && runs.length === 0 ? (
            <div className="text-center py-20">
              <p className="text-red-600 dark:text-red-400 mb-2 transition-colors duration-300">⚠️ {error}</p>
              <p className="text-zinc-600 dark:text-zinc-500 text-sm transition-colors duration-300">Make sure the backend is running on port 8000</p>
            </div>
          ) : filteredRuns.length === 0 ? (
            <div className="text-center py-20">
              <Filter className="w-16 h-16 text-zinc-400 dark:text-zinc-700 mx-auto mb-4 transition-colors duration-300" />
              <h3 className="text-xl font-semibold text-zinc-700 dark:text-zinc-400 mb-2 transition-colors duration-300">
                {searchQuery ? "No matching runs" : "No Test Runs Yet"}
              </h3>
              <p className="text-sm text-zinc-500 dark:text-zinc-600 transition-colors duration-300">
                {searchQuery ? "Try a different search term" : "Run a test from the Lab to start building your evidence vault"}
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredRuns.map((run: any) => (
                <RunCard
                  key={run.id}
                  run={run}
                  onExpand={handleToggleRun}
                  isExpanded={expandedRuns.has(run.id)}
                />
              ))}
            </div>
          )}
        </div>

        <StatusBar
          state="idle"
          onTerminate={() => (window.location.href = "/")}
        />
      </div>
    </main>
  );
}
