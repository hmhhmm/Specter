"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  TrendingUp, 
  MessageCircle, 
  AlertCircle, 
  ArrowUpRight, 
  ArrowDownRight,
  Shield,
  Zap,
  RefreshCw,
  Globe
} from "lucide-react";
import { cn } from "@/lib/utils";

const TRANSLATIONS = {
  en: {
    title: "NovaTrade Pro",
    balance: "Balance",
    confirmTrade: "Confirm Trade",
    sell: "Sell",
    buy: "Buy",
    withdraw: "Withdraw",
    fee: "Transaction Fee",
    amount: "Amount (USD)",
    loading: "Synchronizing with Blockchain...",
    marketStatus: "Market Open",
    price: "Live Price"
  },
  de: {
    title: "NovaHandel Pro",
    balance: "Kontostand",
    confirmTrade: "Handel bestätigen", // LONG TEXT for overflow
    sell: "Verkaufen",
    buy: "Kaufen",
    withdraw: "Auszahlen",
    fee: "Transaktionsgebühr",
    amount: "Betrag (USD)",
    loading: "Synchronisierung mit Blockchain...",
    marketStatus: "Markt Geöffnet",
    price: "Live-Preis"
  }
};

export default function MockTargetPage() {
  const [lang, setLang] = useState<"en" | "de">("en");
  const [price, setPrice] = useState(10420.50); // Large number for overflow
  const [isWithdrawLoading, setIsWithdrawLoading] = useState(false);
  const [showGlobalSpinner, setShowGlobalSpinner] = useState(false);
  const [amount, setAmount] = useState("");

  const t = TRANSLATIONS[lang];

  // Listen for messages from parent (DeviceEmulator)
  useEffect(() => {
    const handleMessage = (e: MessageEvent) => {
      if (e.data.type === "SET_LANG") {
        setLang(e.data.lang);
      } else if (e.data.type === "SHOW_SPINNER") {
        setShowGlobalSpinner(true);
      }
    };
    window.addEventListener("message", handleMessage);
    return () => window.removeEventListener("message", handleMessage);
  }, []);

  const handleWithdraw = () => {
    // Phantom Error: Fails silently
    console.log("Withdraw requested");
  };

  return (
    <div className="min-h-[1200px] bg-[#0a0a0c] text-zinc-100 font-sans p-4 relative overflow-x-hidden select-none">
      {/* Issue 7: Dead-End Spinner (Hidden by default, triggered by demo) */}
      <AnimatePresence>
        {showGlobalSpinner && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="fixed inset-0 z-[10000] bg-black/80 backdrop-blur-md flex flex-col items-center justify-center text-center p-6"
          >
            <RefreshCw className="w-12 h-12 text-emerald-500 animate-spin mb-4" />
            <p className="text-emerald-500 font-mono tracking-widest uppercase">{t.loading}</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header */}
      <header className="flex items-center justify-between mb-8 border-b border-white/5 pb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center">
            <Zap className="text-black w-5 h-5 fill-current" />
          </div>
          <h1 className="text-xl font-bold tracking-tighter">{t.title}</h1>
        </div>

        <div className="flex items-center gap-4">
          <button 
            onClick={() => setLang(lang === "en" ? "de" : "en")}
            className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 hover:bg-white/10 transition-colors text-[10px] font-mono uppercase tracking-widest"
          >
            <Globe className="w-3 h-3" />
            {lang.toUpperCase()}
          </button>
          <div className="text-right">
            <p className="text-[10px] text-zinc-500 uppercase tracking-widest">{t.balance}</p>
            <p className="text-emerald-500 font-bold">$142,500.00</p>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Column: Price Info */}
        <div className="md:col-span-2 space-y-6">
          <div className="p-6 rounded-3xl bg-white/5 border border-white/5">
            <div className="flex justify-between items-start mb-4">
              <div>
                <p className="text-xs text-zinc-500 uppercase tracking-widest mb-1">{t.price}</p>
                {/* Issue 2: Data Overflow - Large text that might wrap */}
                <div className="flex items-baseline gap-3 flex-wrap min-h-[120px]">
                  <span className="text-7xl font-bold tracking-tighter tabular-nums leading-[0.8] py-4">
                    ${price.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </span>
                  <span className="text-emerald-500 flex items-center gap-1 font-bold">
                    <ArrowUpRight className="w-4 h-4" />
                    +2.45%
                  </span>
                </div>
              </div>
              <div className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 text-[10px] uppercase font-bold tracking-widest">
                {t.marketStatus}
              </div>
            </div>
            
            {/* Chart Placeholder */}
            <div className="h-64 w-full bg-white/[0.02] rounded-2xl border border-white/5 relative overflow-hidden">
               <svg viewBox="0 0 400 100" className="absolute bottom-0 w-full h-full opacity-30">
                 <path d="M0 80 Q50 20 100 50 T200 30 T300 70 T400 10" fill="none" stroke="#10b981" strokeWidth="2" />
               </svg>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-2 gap-4">
            <button className="p-4 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-all flex items-center justify-between">
              <span className="font-bold">{t.buy}</span>
              <ArrowUpRight className="text-emerald-500" />
            </button>
            {/* Issue 2 Part 2: Sell button position depends on layout above */}
            <button className="p-4 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-all flex items-center justify-between">
              <span className="font-bold">{t.sell}</span>
              <ArrowDownRight className="text-red-500" />
            </button>
          </div>
        </div>

        {/* Right Column: Trading Form */}
        <div className="space-y-6">
          <div className="p-6 rounded-3xl bg-white/5 border border-white/5 relative">
            <h3 className="font-bold mb-6 text-lg">Execution Panel</h3>
            
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-[10px] text-zinc-500 uppercase tracking-widest">{t.amount}</label>
                {/* Issue 4: Rage Input - uses type="text" instead of numeric inputmode */}
                <input 
                  type="text" 
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  placeholder="0.00"
                  className="w-full bg-black border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-emerald-500 transition-colors tabular-nums"
                />
              </div>

              <div className="flex justify-between items-center py-3 bg-zinc-900 rounded-lg px-3 border border-white/5">
                {/* Issue 3: Invisible Fee - Fixed with high-contrast color */}
                <div className="flex items-center gap-2">
                  <span className="text-[10px] uppercase tracking-widest text-zinc-400">{t.fee}:</span>
                  <span className="text-sm font-bold text-zinc-100">$2.50</span>
                </div>
                <Shield className="w-4 h-4 text-zinc-600" />
              </div>

              {/* Issue 5: Localization Break - Fixed width button so German overflows */}
              <button 
                className="w-[180px] py-4 bg-emerald-500 rounded-xl text-black font-bold hover:bg-emerald-400 transition-colors text-sm px-2 mx-auto block"
              >
                <span className="block whitespace-nowrap">
                  {t.confirmTrade}
                </span>
              </button>
            </div>
          </div>

          {/* Issue 6: Phantom Error - Button that does nothing on click */}
          <button 
            onClick={handleWithdraw}
            className="w-full py-4 rounded-2xl border-2 border-amber-500/50 bg-amber-500/10 hover:bg-amber-500/20 transition-all text-sm font-bold text-amber-500"
          >
            {t.withdraw}
          </button>

          {/* Spacer to ensure scrollability */}
          <div className="h-8" />
        </div>
      </div>

      {/* Footer Branding */}
      <footer className="mt-20 pt-8 border-t border-white/5 flex justify-between items-center">
        <p className="text-[10px] text-zinc-600 font-mono tracking-widest uppercase">NovaTrade v4.2.0-secure</p>
        <div className="flex gap-4 opacity-30">
          <div className="w-4 h-4 bg-zinc-800 rounded-full" />
          <div className="w-4 h-4 bg-zinc-800 rounded-full" />
        </div>
      </footer>

      {/* Issue 1: Z-Index Trap - Chat bubble that covers buttons on small viewports */}
      {/* Positioned fixed but we simulate it in the mobile view of emulator */}
      <div className="fixed bottom-6 right-6 z-[9999] group pointer-events-auto">
        <div className="w-16 h-16 bg-emerald-500 rounded-full shadow-[0_0_30px_rgba(16,185,129,0.4)] flex items-center justify-center cursor-pointer hover:scale-110 transition-transform">
          <MessageCircle className="text-black w-8 h-8 fill-current" />
        </div>
        <div className="absolute bottom-full right-0 mb-4 w-64 bg-zinc-900 border border-white/10 rounded-2xl p-4 shadow-2xl opacity-0 group-hover:opacity-100 transition-opacity">
          <p className="text-xs text-zinc-400 leading-relaxed">
            Hi! Need help with your trade? Our AI assistant is here to help.
          </p>
        </div>
      </div>

      {/* Manual Trigger for Global Spinner (for demo purposes) */}
      <div 
        className="absolute top-0 right-0 w-2 h-2 opacity-0 cursor-pointer" 
        onClick={() => setShowGlobalSpinner(true)}
      />
    </div>
  );
}