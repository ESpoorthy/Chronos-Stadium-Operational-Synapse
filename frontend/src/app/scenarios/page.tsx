"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Zap, Send, Bot, CheckCircle2, AlertCircle } from "lucide-react";
import {
  runSimulation,
  ApiError,
  DEFAULT_STADIUM_DATA,
  type SimulatedFuture,
} from "@/lib/api";

export default function Scenarios() {
  const [query, setQuery] = useState("");
  const [isSimulating, setIsSimulating] = useState(false);
  const [results, setResults] = useState<SimulatedFuture[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSimulate = async () => {
    const trimmed = query.trim();
    if (!trimmed) return;

    setIsSimulating(true);
    setResults(null);
    setError(null);

    try {
      const response = await runSimulation({
        scenario: trimmed,
        stadium_data: DEFAULT_STADIUM_DATA,
      });
      setResults(response.futures);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Unable to connect to the simulation engine. Please ensure the backend is running.");
      }
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="min-h-screen bg-background p-6 lg:p-12">
      <header className="mb-12">
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <Bot className="text-primary" aria-hidden="true" />
          Generative Scenario Engine
        </h1>
        <p className="text-muted-foreground mt-2">
          Query the AI to simulate operational futures in real time.
        </p>
      </header>

      <div className="max-w-4xl mx-auto space-y-8">
        {/* Query Input */}
        <div
          role="search"
          aria-label="Scenario simulation search"
          className="glass-panel p-2 rounded-full flex items-center gap-2 glowing-border"
        >
          <label htmlFor="scenario-query" className="sr-only">
            Enter an operational scenario query
          </label>
          <input
            id="scenario-query"
            type="text"
            className="flex-1 bg-transparent border-none outline-none px-6 py-4 text-lg placeholder:text-muted-foreground/50 focus-visible:outline-none"
            placeholder="What happens if heavy rain starts at 7 PM?"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSimulate()}
            aria-label="Scenario query"
            aria-describedby="query-hint"
            disabled={isSimulating}
            maxLength={2000}
          />
          <p id="query-hint" className="sr-only">
            Type a scenario and press Enter or click Simulate. Max 2000 characters.
          </p>
          <button
            onClick={handleSimulate}
            disabled={isSimulating || !query.trim()}
            aria-label={isSimulating ? "Simulation in progress" : "Run simulation"}
            aria-disabled={isSimulating || !query.trim()}
            className="bg-primary hover:bg-primary/90 text-primary-foreground px-8 py-4 rounded-full font-medium transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background"
          >
            {isSimulating ? (
              <div
                className="animate-spin rounded-full h-5 w-5 border-2 border-white/20 border-t-white"
                role="status"
                aria-label="Loading"
              />
            ) : (
              <Send className="w-5 h-5" aria-hidden="true" />
            )}
            Simulate
          </button>
        </div>

        {/* Loading State */}
        {isSimulating && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center justify-center py-20 text-primary"
            role="status"
            aria-live="polite"
            aria-label="Generating simulated futures, please wait"
          >
            <div className="relative" aria-hidden="true">
              <Zap className="w-16 h-16 animate-pulse" />
              <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full" />
            </div>
            <p className="mt-6 text-lg animate-pulse">Generating simulated futures...</p>
          </motion.div>
        )}

        {/* Error State */}
        {error && !isSimulating && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-start gap-3 p-4 rounded-xl bg-destructive/10 border border-destructive/30 text-destructive"
            role="alert"
            aria-live="assertive"
          >
            <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" aria-hidden="true" />
            <p>{error}</p>
          </motion.div>
        )}

        {/* Results */}
        {results && !isSimulating && (
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            aria-label="Simulation results"
            aria-live="polite"
          >
            <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
              <CheckCircle2 className="text-success" aria-hidden="true" />
              Top Ranked Futures
            </h2>

            <div className="space-y-6">
              {results.map((future, i) => (
                <article
                  key={i}
                  className="glass-panel p-6 rounded-2xl border-l-4"
                  style={{
                    borderLeftColor:
                      future.probability > 50 ? "var(--warning)" : "var(--success)",
                  }}
                  aria-label={`Future ${i + 1}: ${future.description}. Probability: ${future.probability}%. Impact: ${future.operational_impact}.`}
                >
                  <div className="flex justify-between items-start mb-4">
                    <div className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-muted-foreground">
                      Future #{i + 1}
                    </div>
                    <div className="px-4 py-1 rounded-full bg-secondary/80 text-sm font-semibold tracking-wider">
                      Probability: {future.probability}%
                    </div>
                  </div>

                  <p className="text-lg mb-2 text-foreground/90">{future.description}</p>

                  {future.operational_impact && (
                    <p className="text-sm text-muted-foreground mb-4">
                      Impact:{" "}
                      <span className="font-medium text-foreground">
                        {future.operational_impact}
                      </span>
                    </p>
                  )}

                  <div className="bg-primary/10 rounded-xl p-4 border border-primary/20">
                    <h3 className="text-sm uppercase tracking-widest text-primary mb-2">
                      Recommended Action
                    </h3>
                    <p className="font-medium">{future.recommended_decision}</p>
                  </div>
                </article>
              ))}
            </div>
          </motion.section>
        )}
      </div>
    </div>
  );
}
