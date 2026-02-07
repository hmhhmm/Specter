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
            "backdrop-blur-[1px]",
            "ring-1 ring-emerald-500/10",
            "shadow-[0_2px_16px_-2px_rgba(16,185,129,0.1)]",
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
    <section className="relative flex min-h-[85vh] w-full items-center justify-center overflow-hidden bg-zinc-950 pt-32 pb-16">
      <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/[0.05] via-transparent to-zinc-900/[0.05] blur-3xl" />

      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <ElegantShape
          borderRadius={24}
          className="top-[-10%] left-[-15%]"
          delay={0.3}
          gradient="from-emerald-500/[0.15]"
          height={500}
          rotate={-8}
          width={300}
        />

        <ElegantShape
          borderRadius={20}
          className="right-[-20%] bottom-[-5%]"
          delay={0.5}
          gradient="from-zinc-500/[0.1]"
          height={200}
          rotate={15}
          width={600}
        />

        <ElegantShape
          borderRadius={32}
          className="top-[40%] left-[-5%]"
          delay={0.4}
          gradient="from-emerald-600/[0.1]"
          height={300}
          rotate={24}
          width={300}
        />

        <ElegantShape
          borderRadius={12}
          className="top-[5%] right-[10%]"
          delay={0.6}
          gradient="from-emerald-400/[0.08]"
          height={100}
          rotate={-20}
          width={250}
        />
      </div>

      <div className="container relative z-10 mx-auto px-4 md:px-6">
        <div className="mx-auto max-w-4xl text-center">
          <motion.div
            animate="visible"
            custom={1}
            initial="hidden"
            variants={fadeUpVariants}
            className="flex justify-center mb-6"
          >
             <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 font-mono text-xs tracking-wider uppercase">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                Agentic QA Active
             </div>
          </motion.div>

          <motion.div
            animate="visible"
            custom={2}
            initial="hidden"
            variants={fadeUpVariants}
          >
            <h1 className="mb-6 font-bricolage font-bold text-5xl tracking-tighter sm:text-7xl md:mb-8 md:text-8xl text-white">
              The Agent That <span className="bg-gradient-to-r from-emerald-400 via-emerald-200 to-emerald-500 bg-clip-text text-transparent">Feels</span> Your Users&apos; Frustration
            </h1>
          </motion.div>

          <motion.div
            animate="visible"
            custom={3}
            initial="hidden"
            variants={fadeUpVariants}
          >
            <p className="mx-auto mb-8 max-w-2xl px-4 font-mono text-sm text-zinc-500 leading-relaxed tracking-tight sm:text-base md:text-lg">
              Specter.AI is the sentient mystery shopper that navigates your app purely by vision, identifying &quot;Silent Churn&quot;—the friction points standard logs never see.
            </p>
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
                Launch Mystery Shopper
              </GlowButton>
            </Link>
          </motion.div>
        </div>
      </div>

      <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-zinc-950 via-transparent to-zinc-950/80" />
    </section>
  );
}
