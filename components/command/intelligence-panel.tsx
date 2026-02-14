export function IntelligencePanel() {
  const personas = [
    { icon: "⚡", name: "Zoomer", color: "yellow", issue: "2.3s scroll lag detected", severity: "high" },
    { icon: "👵", name: "Boomer", color: "blue", issue: "Font size 9px flagged", severity: "medium" },
    { icon: "🕵️", name: "Skeptic", color: "purple", issue: "Privacy policy hidden", severity: "low" },
    { icon: "💥", name: "Chaos", color: "red", issue: "Validation bypass found", severity: "critical" },
    { icon: "📱", name: "Mobile", color: "green", issue: "Touch target 38px", severity: "medium" }
  ];

  const severityColors = {
    critical: "bg-red-500/20 border-red-500/30 text-red-400",
    high: "bg-orange-500/20 border-orange-500/30 text-orange-400",
    medium: "bg-yellow-500/20 border-yellow-500/30 text-yellow-400",
    low: "bg-emerald-500/20 border-emerald-500/30 text-emerald-400"
  };

  return (
    <div className="rounded-2xl border-2 border-white/10 bg-gradient-to-br from-zinc-900/80 to-zinc-900/40 backdrop-blur-sm p-6 h-full">
      <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
        <span>Persona Intelligence</span>
        <span className="text-xs px-2 py-1 rounded-full bg-emerald-500/20 text-emerald-400">Live</span>
      </h3>
      
      <div className="space-y-3">
        {personas.map((persona) => (
          <div
            key={persona.name}
            className="group relative rounded-xl border-2 border-white/5 bg-white/5 p-4 hover:border-white/10 hover:bg-white/10 transition-all duration-300"
          >
            <div className="flex items-start gap-3">
              <span className="text-2xl">{persona.icon}</span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-semibold text-white">{persona.name}</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${severityColors[persona.severity as keyof typeof severityColors]}`}>
                    {persona.severity}
                  </span>
                </div>
                <p className="text-xs text-zinc-400">{persona.issue}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
