import { Flame } from "lucide-react";
import { Card } from "@/components/ui/card";

interface StreakCounterProps {
  days: number;
  variant?: "compact" | "full";
}

const StreakCounter = ({ days, variant = "full" }: StreakCounterProps) => {
  if (variant === "compact") {
    return (
      <div className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-orange-500/10 to-red-500/10 px-4 py-2 border border-orange-500/20">
        <Flame className="h-5 w-5 text-orange-500 animate-pulse" />
        <span className="text-sm font-bold text-foreground">{days} Day Streak!</span>
      </div>
    );
  }

  return (
    <Card className="gradient-border bg-gradient-to-br from-orange-500/5 to-red-500/5 p-6 shadow-card">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-3xl font-bold text-foreground flex items-center gap-2">
            <Flame className="h-8 w-8 text-orange-500 animate-pulse" />
            {days}
          </div>
          <div className="text-sm text-muted-foreground mt-1">Day Streak 🔥</div>
        </div>
        <div className="text-right">
          <div className="text-sm font-medium text-orange-500">Keep it going!</div>
          <div className="text-xs text-muted-foreground mt-1">You&apos;re on fire</div>
        </div>
      </div>
    </Card>
  );
};

export default StreakCounter;
