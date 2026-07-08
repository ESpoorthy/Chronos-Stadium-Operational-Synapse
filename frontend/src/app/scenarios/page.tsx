"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Zap, Send, Bot, Play, CheckCircle2 } from "lucide-react";

export default function Scenarios() {
  const [query, setQuery] = useState("");
  const [isSimulating, setIsSimulating] = useState(false);
  const [results, setResults] = useState<any>(null);

  const handleSimulate = async () => {
    if (!query) return;
    setIsSimulating(true);
    // Mock simulation delay
    setTimeout(() => {
      setResults({
        futures: [
          {
            prob: 81,
            desc: "Gate C becomes overloaded. Metro congestion increases.",
            impact: "Severe",
            rec: "Open Gate D immediately. Deploy volunteers. Push multilingual notifications."
          },
          {
            prob: 12,
            desc: "Crowd disperses evenly across Gates A and B.",
            impact: "Nominal",
            rec: "Monitor status."
          }
        ]
      });
      setIsSimulating(false);
    }, 2500);
  };

  return (
    <div className="min-h-screen bg-background p-6 lg:p-12">
      <header className="mb-12">
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <Bot className="text-primary" />
          Generative Scenario Engine
        </h1>
        <p className="text-muted-foreground mt-2">Query the AI to simulate operational futures.</p>
      </header>

      <div className="max-w-4xl mx-auto space-y-8">
        <div className="glass-panel p-2 rounded-full flex items-center gap-2 glowing-border">
          <input
            type="text"
            className="flex-1 bg-transparent border-none outline-none px-6 py-4 text-lg placeholder:text-muted-foreground/50"
            placeholder="What happens if heavy rain starts at 7 PM?"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSimulate()}
          />
          <button 
            onClick={handleSimulate}
            disabled={isSimulating}
            className="bg-primary hover:bg-primary/90 text-primary-foreground px-8 py-4 rounded-full font-medium transition-all flex items-center gap-2 disabled:opacity-50"
          >
            {isSimulating ? <div className="animate-spin rounded-full h-5 w-5 border-2 border-white/20 border-t-white" /> : <Send className="w-5 h-5" />}
            Simulate
          </button>
        </div>

        {isSimulating && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center justify-center py-20 text-primary"
          >
            <div className="relative">
              <Zap className="w-16 h-16 animate-pulse" />
              <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full" />
            </div>
            <p className="mt-6 text-lg animate-pulse">Generating 100 simulated futures...</p>
          </motion.div>
        )}

        {results && !isSimulating && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
              <CheckCircle2 className="text-success" />
              Top Ranked Futures
            </h2>
            
            {results.futures.map((future: any, i: number) => (
              <div key={i} className="glass-panel p-6 rounded-2xl border-l-4" style={{ borderLeftColor: future.prob > 50 ? 'var(--warning)' : 'var(--success)' }}>
                <div className="flex justify-between items-start mb-4">
                  <div className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-muted-foreground">
                    Future #{i + 1}
                  </div>
                  <div className="px-4 py-1 rounded-full bg-secondary/80 text-sm font-semibold tracking-wider">
                    Probability: {future.prob}%
                  </div>
                </div>
                
                <p className="text-lg mb-6 text-foreground/90">{future.desc}</p>
                
                <div className="bg-primary/10 rounded-xl p-4 border border-primary/20">
                  <h4 className="text-sm uppercase tracking-widest text-primary mb-2">Recommended Action</h4>
                  <p className="font-medium">{future.rec}</p>
                </div>
              </div>
            ))}
          </motion.div>
        )}
      </div>
    </div>
  );
}
