import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface MoodChipProps {
  icon: LucideIcon;
  label: string;
  isActive: boolean;
  onClick: () => void;
}

const MoodChip = ({ icon: Icon, label, isActive, onClick }: MoodChipProps) => {
  return (
    <button
      onClick={onClick}
      className={cn(
        "relative flex items-center gap-2 rounded-xl px-5 py-3 text-sm font-medium transition-all duration-300",
        isActive
          ? "gradient-primary text-primary-foreground shadow-glow scale-105"
          : "gradient-border bg-card text-muted-foreground hover:scale-105 hover:shadow-md hover:text-foreground"
      )}
    >
      {isActive && (
        <div className="absolute inset-0 bg-white/20 rounded-xl animate-pulse" />
      )}
      <Icon className="h-4 w-4 relative z-10" />
      <span className="relative z-10">{label}</span>
    </button>
  );
};

export default MoodChip;
