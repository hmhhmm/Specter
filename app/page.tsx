import { SpecterNav } from "@/components/landing/specter-nav";
import { HeroSection } from "@/components/landing/hero-section";
import { ProblemGrid } from "@/components/landing/problem-grid";
import { BackgroundEffects } from "@/components/landing/background-effects";

export default function Home() {
  return (
    <main className="min-h-screen bg-white dark:bg-zinc-950 selection:bg-emerald-500/30 selection:text-emerald-200 transition-colors duration-300">
      <BackgroundEffects />
      <div className="relative z-10">
        <SpecterNav />
        <HeroSection />
        <ProblemGrid />
      </div>
      
      {/* Footer Placeholder */}
      <footer className="relative z-10 py-20 border-t border-zinc-200 dark:border-zinc-900 bg-zinc-50/50 dark:bg-zinc-950/50 backdrop-blur-md flex justify-center transition-colors duration-300">
        <div className="flex items-center gap-2 opacity-30">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="font-mono text-xs text-zinc-700 dark:text-zinc-500 tracking-widest uppercase">
            Specter Systems Initialized
          </span>
        </div>
      </footer>
    </main>
  );
}
