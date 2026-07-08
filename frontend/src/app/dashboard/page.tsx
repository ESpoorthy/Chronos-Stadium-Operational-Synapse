"use client";

import { motion } from "framer-motion";
import { Activity, AlertTriangle, Users, CloudRain, ShieldCheck, Zap, Settings, Moon, Sun } from "lucide-react";
import { toast } from "sonner";
import { useTheme } from "next-themes";
import { StadiumMap } from "@/components/StadiumMap";

export default function Dashboard() {
  const { theme, setTheme } = useTheme();

  const handleExecutePlan = () => {
    toast.success("Diversion Plan Alpha Executed!", {
      description: "Volunteers have been deployed to Gate C. Notifications sent to attendees.",
      duration: 5000,
    });
  };

  const handleStreamClick = (streamName: string) => {
    toast.info(`Fetching detailed ${streamName} logs...`, {
      description: "Live connection established.",
    });
  };

  return (
    <div className="min-h-screen bg-background p-6 transition-colors duration-300">
      <header className="flex justify-between items-center mb-8 border-b border-white/5 pb-6">
        <div className="flex items-center gap-2">
          <Zap className="text-primary w-8 h-8" />
          <h1 className="text-2xl font-bold tracking-wider">CHRONOS COMMAND</h1>
        </div>
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2 bg-secondary/50 px-4 py-2 rounded-full cursor-pointer hover:bg-secondary/70 transition-colors" onClick={() => toast.success("System is fully operational")}>
            <div className="w-2 h-2 rounded-full bg-success animate-pulse"></div>
            <span className="text-sm text-muted-foreground uppercase tracking-wider">System Online</span>
          </div>
          
          <button 
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            className="p-3 bg-secondary/50 hover:bg-secondary rounded-full transition-colors"
            title="Toggle Theme"
          >
            {theme === "dark" ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <MetricCard title="Current Stadium Health" value="94%" trend="+2%" icon={<Activity className="text-success" />} />
        <MetricCard title="AI Confidence Score" value="88%" trend="Stable" icon={<ShieldCheck className="text-primary" />} />
        <MetricCard title="Future Predictions" value="124" trend="Active" icon={<Zap className="text-warning" />} />
        <MetricCard title="Risk Level" value="Low" trend="Nominal" icon={<AlertTriangle className="text-muted-foreground" />} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Live Feed */}
        <div className="lg:col-span-2 glass-panel rounded-2xl p-6 h-[500px] flex flex-col">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-primary">Live Operations Map</h2>
            <button className="text-xs flex items-center gap-2 bg-secondary/50 px-3 py-1.5 rounded-full hover:bg-secondary" onClick={() => toast("Map Settings Opened")}>
              <Settings className="w-3 h-3" /> Map Settings
            </button>
          </div>
          <div className="flex-1 rounded-xl bg-secondary/20 border border-white/5 relative overflow-hidden">
            <StadiumMap />
          </div>
        </div>

        {/* Intelligence Sidebar */}
        <div className="glass-panel rounded-2xl p-6 flex flex-col gap-6">
          <h2 className="text-xl font-semibold text-primary">Intelligence Streams</h2>
          
          <StreamItem onClick={() => handleStreamClick("Crowd Density")} icon={<Users className="text-primary" />} title="Crowd Density" value="42,510" status="Optimal" />
          <StreamItem onClick={() => handleStreamClick("Weather")} icon={<CloudRain className="text-warning" />} title="Weather" value="Light Rain" status="Monitoring" />
          <StreamItem onClick={() => handleStreamClick("Transit")} icon={<Activity className="text-success" />} title="Transit" value="Flowing" status="Clear" />
          
          <div className="mt-auto border-t border-white/5 pt-6">
            <h3 className="text-sm uppercase text-muted-foreground tracking-widest mb-4">Latest AI Recommendation</h3>
            <div className="bg-primary/10 border border-primary/20 rounded-xl p-4 transition-all hover:bg-primary/20 hover:scale-[1.02]">
              <p className="text-sm font-medium mb-4">Gate C Congestion Predicted in 15m</p>
              <button 
                onClick={handleExecutePlan}
                className="text-xs bg-primary text-primary-foreground px-4 py-3 rounded-full uppercase tracking-wider font-bold w-full hover:bg-primary/90 transition-colors shadow-[0_0_15px_rgba(79,140,255,0.4)] hover:shadow-[0_0_25px_rgba(79,140,255,0.6)]"
              >
                Execute Diversion Plan Alpha
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, trend, icon }: { title: string, value: string, trend: string, icon: React.ReactNode }) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel p-6 rounded-2xl glowing-border group cursor-default"
    >
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-sm text-muted-foreground uppercase tracking-widest">{title}</h3>
        <div className="group-hover:scale-110 transition-transform">{icon}</div>
      </div>
      <div className="flex items-end justify-between">
        <span className="text-3xl font-bold">{value}</span>
        <span className="text-xs text-muted-foreground">{trend}</span>
      </div>
    </motion.div>
  );
}

function StreamItem({ icon, title, value, status, onClick }: { icon: React.ReactNode, title: string, value: string, status: string, onClick?: () => void }) {
  return (
    <div onClick={onClick} className="flex items-center gap-4 p-4 rounded-xl bg-secondary/30 border border-white/5 hover:bg-secondary/70 transition-colors cursor-pointer group">
      <div className="p-2 rounded-lg bg-background/50 group-hover:scale-110 transition-transform">
        {icon}
      </div>
      <div className="flex-1">
        <h4 className="text-sm font-medium">{title}</h4>
        <div className="text-xs text-muted-foreground">{status}</div>
      </div>
      <div className="text-sm font-bold text-right">
        {value}
      </div>
    </div>
  );
}
