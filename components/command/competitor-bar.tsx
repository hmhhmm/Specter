import { TrendingDown } from "lucide-react";

export function CompetitorBar() {
  return (
    <div className="rounded-2xl border-2 border-zinc-200 dark:border-white/10 bg-gradient-to-br from-white to-zinc-50 dark:from-zinc-900/80 dark:to-zinc-900/40 backdrop-blur-sm p-6 transition-colors duration-300">
      <h3 className="text-lg font-bold mb-6">Competitive Analysis</h3>
      
      <div className="space-y-6">
        <div>
          <div className="flex items-center justify-between mb-3">
            <div>
              <span className="text-sm text-zinc-700 dark:text-zinc-400">Your Product</span>
              <p className="text-xs text-zinc-500 dark:text-zinc-600 mt-0.5">UX Quality Score</p>
            </div>
            <span className="text-3xl font-bold text-yellow-500 dark:text-yellow-400">72</span>
          </div>
          <div className="relative h-3 bg-zinc-200 dark:bg-white/5 rounded-full overflow-hidden">
            <div className="absolute inset-y-0 left-0 bg-gradient-to-r from-yellow-500 to-yellow-600 rounded-full" style={{width: '72%'}} />
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-3">
            <div>
              <span className="text-sm text-zinc-700 dark:text-zinc-400">Industry Leader</span>
              <p className="text-xs text-zinc-500 dark:text-zinc-600 mt-0.5">Benchmark Score</p>
            </div>
            <span className="text-3xl font-bold text-emerald-500 dark:text-emerald-400">89</span>
          </div>
          <div className="relative h-3 bg-zinc-200 dark:bg-white/5 rounded-full overflow-hidden">
            <div className="absolute inset-y-0 left-0 bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-full" style={{width: '89%'}} />
          </div>
        </div>

        <div className="pt-4 border-t border-zinc-200 dark:border-white/10">
          <div className="flex items-center gap-2 text-red-500 dark:text-red-400">
            <TrendingDown className="w-4 h-4" />
            <span className="text-sm font-semibold">17 points below industry leader</span>
          </div>
          <p className="text-xs text-zinc-500 dark:text-zinc-500 mt-2">
            Primary gaps: Mobile UX (12 pts), Accessibility (5 pts)
          </p>
        </div>
      </div>
    </div>
  );
}
