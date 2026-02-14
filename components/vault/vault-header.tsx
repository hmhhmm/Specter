interface VaultHeaderProps {
  totalIncidents?: number;
}

export function VaultHeader({ totalIncidents = 0 }: VaultHeaderProps) {
  return (
    <div className="mb-12">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-1 h-8 bg-gradient-to-b from-emerald-500 to-emerald-600 rounded-full" />
          <h1 className="text-4xl font-bold tracking-tight">Evidence Vault</h1>
          {totalIncidents > 0 && (
            <div className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">
              <span className="text-sm font-semibold text-emerald-400">{totalIncidents} incidents</span>
            </div>
          )}
        </div>
      </div>
      <p className="text-zinc-400 text-sm ml-4">Forensic archive of all QA incidents, screenshots, and diagnostic reports</p>
    </div>
  );
}
