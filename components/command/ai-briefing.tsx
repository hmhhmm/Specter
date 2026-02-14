interface AIBriefingProps {
  totalTests?: number;
  issuesFound?: number;
  uptime?: string;
  revenueLoss?: number;
}

export function AIBriefing({ 
  totalTests = 0, 
  issuesFound = 0, 
  uptime = "0%",
  revenueLoss = 0 
}: AIBriefingProps) {
  return (
    <div className="relative rounded-3xl border-2 border-white/10 bg-gradient-to-br from-zinc-900/80 to-zinc-900/40 backdrop-blur-xl p-10 mb-12 overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl" />
      
      <div className="relative z-10">
        <div className="flex items-center gap-3 mb-6">
          <div className="relative">
            <div className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse" />
            <div className="absolute inset-0 w-3 h-3 rounded-full bg-emerald-500 animate-ping" />
          </div>
          <span className="text-xs uppercase tracking-[0.2em] text-emerald-400 font-semibold">Live System Status</span>
        </div>
        
        <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-white to-zinc-400 bg-clip-text text-transparent">
          Autonomous QA Dashboard
        </h2>
        
        <p className="text-base text-zinc-400 leading-relaxed max-w-3xl">
          Real-time intelligence from Claude Sonnet 4 analyzing user flows across 5 behavioral personas. 
          Surfacing critical UX failures, revenue blockers, and accessibility violations before they reach production.
        </p>

        <div className="grid grid-cols-4 gap-6 mt-8">
          <div className="rounded-xl bg-white/5 p-4 border border-white/10">
            <p className="text-xs text-zinc-500 uppercase tracking-wider mb-2">Total Tests</p>
            <p className="text-2xl font-bold text-white">{totalTests.toLocaleString()}</p>
          </div>
          <div className="rounded-xl bg-white/5 p-4 border border-white/10">
            <p className="text-xs text-zinc-500 uppercase tracking-wider mb-2">Issues Found</p>
            <p className="text-2xl font-bold text-red-400">{issuesFound.toLocaleString()}</p>
          </div>
          <div className="rounded-xl bg-white/5 p-4 border border-white/10">
            <p className="text-xs text-zinc-500 uppercase tracking-wider mb-2">Revenue Loss</p>
            <p className="text-2xl font-bold text-orange-400">${(revenueLoss / 1000).toFixed(0)}k</p>
          </div>
          <div className="rounded-xl bg-white/5 p-4 border border-white/10">
            <p className="text-xs text-zinc-500 uppercase tracking-wider mb-2">Uptime</p>
            <p className="text-2xl font-bold text-emerald-400">{uptime}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
