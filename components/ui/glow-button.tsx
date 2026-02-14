"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { ReactNode } from "react";

interface GlowButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  className?: string;
}

export function GlowButton({ children, className, ...props }: GlowButtonProps) {
  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className="relative group"
    >
      <div className="absolute -inset-0.5 bg-gradient-to-r from-emerald-500 to-green-600 rounded-full blur opacity-30 group-hover:opacity-100 transition duration-1000 group-hover:duration-200"></div>
      <Button
        className={cn(
          "relative px-8 py-6 bg-zinc-950 hover:bg-zinc-900 text-white border border-emerald-500/20 rounded-full font-mono tracking-tight text-lg",
          className
        )}
        {...props}
      >
        <span className="flex items-center gap-2">
          {children}
        </span>
      </Button>
    </motion.div>
  );
}
