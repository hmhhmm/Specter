import { Globe } from "lucide-react";

export function RegionalMap() {
  const regions = [
    { name: "North America", rate: 65, color: "red", gradient: "from-red-500 to-red-600" },
    { name: "Europe", rate: 42, color: "orange", gradient: "from-orange-500 to-orange-600" },
    { name: "Asia Pacific", rate: 28, color: "yellow", gradient: "from-yellow-500 to-yellow-600" },
    { name: "Latin America", rate: 18, color: "emerald", gradient: "from-emerald-500 to-emerald-600" }
  ];

  return (
    <div className="rounded-2xl border-2 border-zinc-200 dark:border-white/10 bg-gradient-to-br from-white to-zinc-50 dark:from-zinc-900/80 dark:to-zinc-900/40 backdrop-blur-sm p-6 transition-colors duration-300">
      <div className="flex items-center gap-2 mb-6">
        <Globe className="w-5 h-5 text-zinc-600 dark:text-zinc-400" />
        <h3 className="text-lg font-bold">Geographic Distribution</h3>
      </div>
      
      <div className="space-y-5">
        {regions.map((region) => (
          <div key={region.name}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-zinc-700 dark:text-zinc-300">{region.name}</span>
              <div className="flex items-center gap-3">
                <div className="w-32 h-2 bg-zinc-200 dark:bg-white/5 rounded-full overflow-hidden">
                  <div 
                    className={`h-full bg-gradient-to-r ${region.gradient} rounded-full transition-all duration-500`}
                    style={{width: `${region.rate}%`}}
                  />
                </div>
                <span className={`text-sm font-bold font-mono text-${region.color}-400 w-12 text-right`}>
                  {region.rate}%
                </span>
              </div>
            </div>
          </div>
        ))}

        <div className="pt-4 mt-4 border-t border-zinc-200 dark:border-white/10">
          <p className="text-xs text-zinc-500 dark:text-zinc-500">
            Failure rate by region over last 24 hours
          </p>
        </div>
      </div>
    </div>
  );
}
