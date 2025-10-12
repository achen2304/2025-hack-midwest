import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { LucideIcon } from "lucide-react";

interface ProgressCardProps {
  title: string;
  value: number;
  total: number;
  icon: LucideIcon;
  color?: "primary" | "accent" | "success";
  message?: string;
}

const ProgressCard = ({ title, value, total, icon: Icon, color = "primary", message }: ProgressCardProps) => {
  const percentage = Math.round((value / total) * 100);
  
  const colorClasses = {
    primary: "text-primary bg-primary/10",
    accent: "text-accent bg-accent/10",
    success: "text-success bg-success/10",
  };

  return (
    <Card className="border-border bg-card p-6 shadow-card hover:shadow-card-hover transition-all duration-300">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`p-3 rounded-xl ${colorClasses[color]}`}>
            <Icon className="h-5 w-5" />
          </div>
          <div>
            <div className="text-sm font-medium text-muted-foreground">{title}</div>
            <div className="text-2xl font-bold text-foreground mt-1">
              {value}/{total}
            </div>
          </div>
        </div>
      </div>
      <Progress value={percentage} className="h-2 mb-2" />
      {message && (
        <p className="text-xs text-muted-foreground italic mt-2">{message}</p>
      )}
    </Card>
  );
};

export default ProgressCard;
