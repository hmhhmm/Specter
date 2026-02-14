export function HealingHub() {
  return (
    <div className="rounded-2xl border-2 border-zinc-200 dark:border-white/10 bg-gradient-to-br from-white to-zinc-50 dark:from-zinc-900/80 dark:to-zinc-900/40 backdrop-blur-sm p-6 h-full transition-colors duration-300">
      <h3 className="text-lg font-bold mb-6">Auto-Remediation</h3>
      
      <div className="space-y-4">
        <div className="group relative rounded-xl border-2 border-emerald-500/30 bg-gradient-to-br from-emerald-500/10 to-emerald-600/10 p-4 hover:border-emerald-500/50 transition-all">
          <div className="flex items-start gap-3">
            <div className="mt-1">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">Ready to Deploy</span>
              </div>
              <p className="text-sm text-zinc-700 dark:text-zinc-200 font-medium mb-1">Reduce z-index to 100</p>
              <p className="text-xs text-zinc-600 dark:text-zinc-400">ChatWidget.tsx • Line 47</p>
            </div>
          </div>
        </div>

        <div className="rounded-xl border-2 border-zinc-200 dark:border-white/5 bg-zinc-100 dark:bg-white/5 p-4 hover:border-zinc-300 dark:hover:border-white/10 transition-all">
          <div className="flex items-start gap-3">
            <div className="mt-1">
              <div className="w-2 h-2 rounded-full bg-zinc-400 dark:bg-zinc-500" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs font-semibold text-zinc-600 dark:text-zinc-400 uppercase tracking-wider">Suggested</span>
              </div>
              <p className="text-sm text-zinc-800 dark:text-zinc-300 font-medium mb-1">Add keyboard escape handler</p>
              <p className="text-xs text-zinc-500 dark:text-zinc-500">PaymentModal.tsx • Line 128</p>
            </div>
          </div>
        </div>

        <div className="rounded-xl border-2 border-zinc-200 dark:border-white/5 bg-zinc-100 dark:bg-white/5 p-4 hover:border-zinc-300 dark:hover:border-white/10 transition-all">
          <div className="flex items-start gap-3">
            <div className="mt-1">
              <div className="w-2 h-2 rounded-full bg-zinc-400 dark:bg-zinc-500" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs font-semibold text-zinc-600 dark:text-zinc-400 uppercase tracking-wider">Recommended</span>
              </div>
              <p className="text-sm text-zinc-800 dark:text-zinc-300 font-medium mb-1">Increase min font size</p>
              <p className="text-xs text-zinc-500 dark:text-zinc-500">globals.css • Line 12</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
