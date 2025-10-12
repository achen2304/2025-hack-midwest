import { Progress } from "@/components/ui/progress";
import { Sparkles } from "lucide-react";

interface XPBarProps {
  currentXP: number;
  nextLevelXP: number;
  level: number;
}

const XPBar = ({ currentXP, nextLevelXP, level }: XPBarProps) => {
  const percentage = (currentXP / nextLevelXP) * 100;

  return (
    <div className="rounded-xl bg-card border border-border p-4 shadow-sm">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-accent" />
          <span className="text-sm font-semibold text-foreground">Level {level}</span>
        </div>
        <span className="text-xs text-muted-foreground">
          {currentXP} / {nextLevelXP} XP
        </span>
      </div>
      <Progress value={percentage} className="h-2" />
    </div>
  );
};

export default XPBar;
