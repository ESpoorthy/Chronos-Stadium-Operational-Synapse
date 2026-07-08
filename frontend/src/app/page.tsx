"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { ArrowRight, Activity, Zap, Shield, Cpu } from "lucide-react";

export default function Home() {
  return (
    <main
      className="min-h-screen bg-background text-foreground overflow-hidden relative"
      aria-label="Chronos Stadium AI home page"
    >
      {/* Decorative background effects — hidden from assistive technologies */}
      <div className="absolute inset-0 z-0" aria-hidden="true">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-[120px]" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-success/10 rounded-full blur-[120px]" />
      </div>

      <div className="container mx-auto px-6 py-24 relative z-10">
        <nav aria-label="Main navigation" className="flex justify-between items-center mb-24">
          <div className="text-2xl font-bold tracking-tighter flex items-center gap-2" aria-label="Chronos AI logo">
            <Zap className="text-primary" aria-hidden="true" />
            CHRONOS<span className="text-primary">.AI</span>
          </div>
          <Link
            href="/dashboard"
            aria-label="Enter the Chronos operations dashboard"
            className="px-6 py-2 rounded-full border border-primary/30 hover:border-primary transition-colors text-sm uppercase tracking-widest text-primary glowing-border focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background"
          >
            Enter Dashboard
          </Link>
        </nav>

        <div className="flex flex-col items-center text-center max-w-4xl mx-auto mt-20">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-5xl md:text-7xl font-bold tracking-tighter mb-6 bg-clip-text text-transparent bg-gradient-to-r from-white via-blue-100 to-primary">
              Chronos Stadium AI
            </h1>
            <p className="text-xl md:text-2xl text-muted-foreground mb-12 font-light">
              The world&apos;s first <span className="text-white font-medium">Generative Future Engine</span> for Mega Events.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="flex gap-4"
          >
            <Link
              href="/dashboard"
              aria-label="Initialize stadium operations — go to the dashboard"
              className="flex items-center gap-2 px-8 py-4 bg-primary text-primary-foreground rounded-full font-medium hover:bg-primary/90 transition-all hover:scale-105 active:scale-95 shadow-[0_0_20px_rgba(79,140,255,0.4)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background"
            >
              Initialize Operations <ArrowRight className="w-4 h-4" aria-hidden="true" />
            </Link>
          </motion.div>
        </div>

        <motion.section
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-32"
          aria-label="Key platform features"
        >
          <FeatureCard
            icon={<Cpu className="w-8 h-8 text-primary" aria-hidden="true" />}
            title="Future Simulation"
            description="Continuously generates hundreds of possible operational scenarios from live stadium data."
          />
          <FeatureCard
            icon={<Activity className="w-8 h-8 text-success" aria-hidden="true" />}
            title="Live Intelligence"
            description="Real-time tracking of crowd density, transit flow, and environmental metrics."
          />
          <FeatureCard
            icon={<Shield className="w-8 h-8 text-warning" aria-hidden="true" />}
            title="Proactive Defense"
            description="Identifies risks before they occur and recommends optimal operational decisions."
          />
        </motion.section>
      </div>
    </main>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <article
      className="glass-panel p-8 rounded-2xl flex flex-col items-start text-left glowing-border transition-all hover:-translate-y-2 cursor-default group"
      aria-label={`Feature: ${title}`}
    >
      <div className="mb-6 p-4 rounded-xl bg-background/50 group-hover:scale-110 transition-transform">
        {icon}
      </div>
      <h2 className="text-xl font-semibold mb-3">{title}</h2>
      <p className="text-muted-foreground leading-relaxed">{description}</p>
    </article>
  );
}
