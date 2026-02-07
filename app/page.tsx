import { SpecterNav } from "@/components/landing/specter-nav";
import { HeroSection } from "@/components/landing/hero-section";
import { ProblemGrid } from "@/components/landing/problem-grid";

export default function Home() {
  return (
    <main className="min-h-screen bg-zinc-950 selection:bg-emerald-500/30 selection:text-emerald-200">
      <SpecterNav />
      <HeroSection />
      <ProblemGrid />
      
      {/* Footer Placeholder */}
      <footer className="py-20 border-t border-zinc-900 bg-zinc-950 flex justify-center">
        <div className="flex items-center gap-2 opacity-30">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="font-mono text-xs text-zinc-500 tracking-widest uppercase">
            Specter Systems Initialized
          </span>
        </div>
      </footer>
    </main>
  );
}
