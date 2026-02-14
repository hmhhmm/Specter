import { FileCode2, Users } from "lucide-react";

export function RootCausePanel() {
  const issues = [
    { severity: "P0", file: "ChatWidget.tsx", line: 47, owner: "frontend-team", color: "red" },
    { severity: "P0", file: "PaymentModal.tsx", line: 128, owner: "checkout-team", color: "red" },
    { severity: "P1", file: "LocaleSwitch.tsx", line: 89, owner: "i18n-team", color: "orange" },
    { severity: "P2", file: "PriceDisplay.tsx", line: 34, owner: "design-system", color: "yellow" }
  ];

  const colorMap = {
    red: "from-red-500/20 to-red-600/20 border-red-500/30 text-red-400",
    orange: "from-orange-500/20 to-orange-600/20 border-orange-500/30 text-orange-400",
    yellow: "from-yellow-500/20 to-yellow-600/20 border-yellow-500/30 text-yellow-400"
  };

  return (
    <div className="rounded-2xl border-2 border-zinc-200 dark:border-white/10 bg-gradient-to-br from-white to-zinc-50 dark:from-zinc-900/80 dark:to-zinc-900/40 backdrop-blur-sm p-6 transition-colors duration-300">
      <h3 className="text-lg font-bold mb-6">Root Cause Tracing</h3>
      
      <div className="space-y-3">
        {issues.map((issue, i) => (
          <div
            key={i}
            className="group rounded-xl border-2 border-zinc-200 dark:border-white/5 bg-zinc-100 dark:bg-white/5 p-4 hover:border-zinc-300 dark:hover:border-white/10 hover:bg-zinc-200 dark:hover:bg-white/10 transition-all"
          >
            <div className="flex items-start gap-4">
              <div className={`px-2.5 py-1 rounded-lg text-xs font-bold border-2 bg-gradient-to-br ${colorMap[issue.color as keyof typeof colorMap]}`}>
                {issue.severity}
              </div>
              <div className="flex-1 space-y-2">
                <div className="flex items-center gap-2">
                  <FileCode2 className="w-4 h-4 text-zinc-600 dark:text-zinc-400" />
                  <span className="text-sm font-mono text-zinc-900 dark:text-white">{issue.file}</span>
                  <span className="text-xs text-zinc-500 dark:text-zinc-500">L{issue.line}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Users className="w-3 h-3 text-zinc-500 dark:text-zinc-500" />
                  <span className="text-xs text-zinc-600 dark:text-zinc-400">@{issue.owner}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
