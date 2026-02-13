"use client";

import { motion } from "framer-motion";
import { Ghost, Database, LayoutDashboard, Microscope } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

export function SpecterNav() {
  const pathname = usePathname();

  const navLinks = [
    { name: "Lab", href: "/lab", icon: Microscope },
    { name: "Vault", href: "/vault", icon: Database },
    { name: "Command", href: "/command", icon: LayoutDashboard },
  ];

  return (
    <motion.nav
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.8, ease: "circOut" }}
      className="fixed top-0 left-0 right-0 z-50 flex justify-center p-6"
    >
      <div className="flex items-center justify-between w-full max-w-7xl px-6 py-3 bg-zinc-950/60 backdrop-blur-xl border border-zinc-800/50 rounded-full shadow-xl">
        <Link href="/" className="transition-opacity hover:opacity-80">
          <span className="font-bricolage text-xl font-bold tracking-tight text-white">
            Specter
          </span>
        </Link>

        <div className="hidden md:flex items-center gap-2 text-zinc-400 font-mono text-xs">
          {navLinks.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link 
                key={link.href}
                href={link.href} 
                className={cn(
                  "flex items-center gap-2 px-4 py-2 rounded-full transition-all duration-300",
                  isActive 
                    ? "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20" 
                    : "hover:text-emerald-400 hover:bg-white/5 border border-transparent"
                )}
              >
                <link.icon className={cn("w-3.5 h-3.5", isActive ? "text-emerald-500" : "text-zinc-500 group-hover:text-emerald-400")} />
                {link.name}
              </Link>
            );
          })}
        </div>

        <div className="flex items-center">
          <button className="px-6 py-2 rounded-full text-zinc-400 font-mono text-sm hover:text-white hover:bg-white/5 transition-all duration-300">
            Login
          </button>
        </div>
      </div>
    </motion.nav>
  );
}
