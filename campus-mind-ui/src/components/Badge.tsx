import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface BadgeProps {
  icon: LucideIcon;
  title: string;
  description?: string;
  unlocked?: boolean;
  size?: "sm" | "md" | "lg";
}

const Badge = ({ icon: Icon, title, description, unlocked = true, size = "md" }: BadgeProps) => {
  const sizes = {
    sm: "h-12 w-12",
    md: "h-16 w-16",
    lg: "h-20 w-20",
  };

  return (
    <div className="flex flex-col items-center gap-2 group">
      <div
        className={cn(
          "rounded-2xl flex items-center justify-center transition-all duration-300",
          sizes[size],
          unlocked
            ? "gradient-primary shadow-glow hover:scale-110"
            : "bg-muted/50 opacity-40 grayscale"
        )}
      >
        <Icon className={cn("text-primary-foreground", size === "sm" ? "h-6 w-6" : size === "md" ? "h-8 w-8" : "h-10 w-10")} />
      </div>
      <div className="text-center">
        <div className={cn("text-sm font-semibold", unlocked ? "text-foreground" : "text-muted-foreground")}>
          {title}
        </div>
        {description && (
          <div className="text-xs text-muted-foreground mt-1">{description}</div>
        )}
      </div>
    </div>
  );
};

export default Badge;
