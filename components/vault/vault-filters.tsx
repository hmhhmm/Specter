interface VaultFiltersProps {
  activeFilter: string;
  onFilterChange: (filter: string) => void;
}

export function VaultFilters({ activeFilter, onFilterChange }: VaultFiltersProps) {
  const filters = [
    { id: "all", label: "All Issues" },
    { id: "p0", label: "P0" },
    { id: "p1", label: "P1" },
    { id: "p2", label: "P2" },
    { id: "mobile", label: "Mobile" },
    { id: "desktop", label: "Desktop" }
  ];

  return (
    <div className="flex flex-wrap gap-3 mb-10">
      {filters.map((filter) => (
        <button
          key={filter.id}
          onClick={() => onFilterChange(filter.id)}
          className={`group relative px-6 py-3 rounded-xl text-sm font-medium transition-all duration-300 ${
            activeFilter === filter.id
              ? "bg-gradient-to-br from-emerald-500/20 to-emerald-600/20 text-emerald-400 border-2 border-emerald-500/50 shadow-lg shadow-emerald-500/20"
              : "bg-zinc-900/60 text-zinc-400 border-2 border-white/5 hover:border-white/10 hover:bg-zinc-900/80"
          }`}
        >
          <span className="relative z-10">
            {filter.label}
          </span>
        </button>
      ))}
    </div>
  );
}
