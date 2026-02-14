import { TrendingDown } from "lucide-react";

export function FScoreWave() {
  const runs = [
    { id: "#1247", score: 85, color: "emerald" },
    { id: "#1248", score: 82, color: "emerald" },
    { id: "#1249", score: 75, color: "yellow" },
    { id: "#1250", score: 72, color: "yellow" }
  ];

  return (
    <div className="rounded-2xl border-2 border-zinc-200 dark:border-white/10 bg-gradient-to-br from-white to-zinc-50 dark:from-zinc-900/80 dark:to-zinc-900/40 backdrop-blur-sm p-6 transition-colors duration-300">
      <h3 className="text-lg font-bold mb-6">Quality Score Trend</h3>
      
      <div className="space-y-6">
        <div>
          <div className="flex items-baseline gap-3 mb-2">
            <span className="text-5xl font-bold text-yellow-500 dark:text-yellow-400">72</span>
            <div className="flex items-center gap-2">
              <TrendingDown className="w-4 h-4 text-red-500 dark:text-red-400" />
              <span className="text-sm text-red-500 dark:text-red-400 font-semibold">-8 from last run</span>
            </div>
          </div>
          <p className="text-xs text-zinc-500 dark:text-zinc-500">Current F-Score</p>
        </div>

        <div>
          <div className="flex justify-between text-xs text-zinc-500 mb-3">
            {runs.map((run) => (
              <span key={run.id}>{run.id}</span>
            ))}
          </div>
          <div className="flex items-end gap-2 h-32">
            {runs.map((run, i) => (
              <div key={run.id} className="flex-1 flex flex-col items-center gap-2">
                <div 
                  className={`w-full bg-gradient-to-t from-${run.color}-500/30 to-${run.color}-500/20 rounded-t-lg border-2 border-${run.color}-500/30 transition-all duration-500`}
                  style={{height: `${run.score}%`}}
                />
                <span className={`text-xs font-bold ${i === runs.length - 1 ? `text-${run.color}-400` : 'text-zinc-500'}`}>
                  {run.score}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="pt-4 border-t border-zinc-200 dark:border-white/10">
          <p className="text-xs text-zinc-500 dark:text-zinc-500">
            Test #1250 • 13 issues detected • 2 critical
          </p>
        </div>
      </div>
    </div>
  );
}
