"use client";

import { motion, Variants } from "framer-motion";
import { cn } from "@/lib/utils";
import { GlowButton } from "@/components/ui/glow-button";
import { ScanSearch } from "lucide-react";
import Link from "next/link";

function ElegantShape({
  className,
  delay = 0,
  width = 400,
  height = 100,
  rotate = 0,
  gradient = "from-emerald-500/[0.08]",
  borderRadius = 16,
}: {
  className?: string;
  delay?: number;
  width?: number;
  height?: number;
  rotate?: number;
  gradient?: string;
  borderRadius?: number;
}) {
  return (
    <motion.div
      animate={{
        opacity: 1,
        y: 0,
        rotate,
      }}
      className={cn("absolute", className)}
      initial={{
        opacity: 0,
        y: -150,
        rotate: rotate - 15,
      }}
      transition={{
        duration: 2.4,
        delay,
        ease: [0.23, 0.86, 0.39, 0.96],
        opacity: { duration: 1.2 },
      }}
    >
      <motion.div
        animate={{
          y: [0, 15, 0],
        }}
        className="relative"
        style={{
          width,
          height,
          borderRadius,
        }}
        transition={{
          duration: 12,
          repeat: Number.POSITIVE_INFINITY,
          ease: "easeInOut",
        }}
      >
        <div
          className={cn(
            "absolute inset-0",
            "bg-gradient-to-r to-transparent",
            gradient,
            "backdrop-blur-[2px]",
            "ring-1 ring-emerald-500/20",
            "shadow-[0_2px_32px_-2px_rgba(16,185,129,0.2)]",
            "after:absolute after:inset-0",
            "after:bg-[radial-gradient(circle_at_50%_50%,rgba(16,185,129,0.1),transparent_70%)]",
            "after:rounded-[inherit]"
          )}
          style={{ borderRadius }}
        />
      </motion.div>
    </motion.div>
  );
}

export function HeroSection() {
  const fadeUpVariants: Variants = {
    hidden: { opacity: 0, y: 30 },
    visible: (i: number) => ({
      opacity: 1,
      y: 0,
      transition: {
        duration: 1,
        delay: 0.5 + (typeof i === 'number' ? i : 0) * 0.2,
        ease: [0.25, 0.4, 0.25, 1],
      },
    }),
  };

  return (
    <section className="relative flex min-h-screen w-full items-center justify-center overflow-hidden bg-transparent">
      <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/[0.15] via-transparent to-zinc-900/[0.15] blur-3xl opacity-70" />

      <div className="container relative z-10 mx-auto px-4 md:px-6">
        <div className="mx-auto max-w-4xl text-center mt-16">
          <motion.div
            animate="visible"
            custom={2}
            initial="hidden"
            variants={fadeUpVariants}
          >
            <h1 className="mb-6 font-bricolage font-bold text-5xl tracking-tighter sm:text-6xl md:mb-8 md:text-7xl text-zinc-900 dark:text-white transition-colors duration-300">
              The Agent That <span className="bg-gradient-to-r from-emerald-600 via-emerald-500 to-emerald-600 dark:from-emerald-400 dark:via-emerald-200 dark:to-emerald-500 bg-clip-text text-transparent">Feels</span> Your Users&apos; Frustration
            </h1>
          </motion.div>

          <motion.div
            animate="visible"
            custom={3}
            initial="hidden"
            variants={fadeUpVariants}
          >
            <p className="mx-auto mb-8 max-w-2xl px-4 font-mono text-sm text-zinc-600 dark:text-zinc-500 leading-relaxed tracking-tight sm:text-base md:text-lg transition-colors duration-300">
            An autonomous mystery shopper that experiences app like a real user and uncovers hidden friction beyond standard logs</p>
          </motion.div>

          <motion.div
            animate="visible"
            custom={4}
            initial="hidden"
            variants={fadeUpVariants}
            className="flex justify-center"
          >
            <Link href="/lab">
              <GlowButton className="px-10 py-8 text-xl">
                <ScanSearch className="w-6 h-6" />
                Start Testing Session
              </GlowButton>
            </Link>
          </motion.div>
        </div>
      </div>

      <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-white dark:from-zinc-950 via-transparent to-white/80 dark:to-zinc-950/80 transition-colors duration-300" />
    </section>
  );
}
