import { Clock, BookOpen, Heart } from "lucide-react";
import { Card } from "@/components/ui/card";

interface PlanCardProps {
  type: "study" | "wellness";
  title: string;
  subtitle?: string;
  time: string;
  duration?: string;
  priority?: "low" | "medium" | "high";
}

const PlanCard = ({ type, title, subtitle, time, duration, priority }: PlanCardProps) => {
  const getPriorityColor = () => {
    switch (priority) {
      case "high":
        return "bg-warning/10 border-warning/30 text-warning";
      case "medium":
        return "bg-primary/10 border-primary/30 text-primary";
      case "low":
        return "bg-success/10 border-success/30 text-success";
      default:
        return "bg-muted";
    }
  };

  return (
    <Card className="group relative overflow-hidden gradient-border bg-card transition-all duration-300 hover:-translate-y-2 hover:shadow-glow">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-accent/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      
      <div className="relative flex items-start gap-4 p-5">
        <div className="relative">
          <div className={`absolute inset-0 blur-lg ${type === "study" ? "bg-primary/30" : "bg-accent/30"} rounded-xl`} />
          <div
            className={`relative mt-1 flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${
              type === "study" ? "gradient-primary" : "bg-gradient-to-br from-accent to-accent-glow"
            } shadow-lg`}
          >
            {type === "study" ? (
              <BookOpen className="h-5 w-5 text-white" />
            ) : (
              <Heart className="h-5 w-5 text-white" />
            )}
          </div>
        </div>

        <div className="flex-1 space-y-1.5">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors">{title}</h3>
            {priority && (
              <span className={`rounded-full border px-2.5 py-1 text-xs font-medium ${getPriorityColor()}`}>
                {priority}
              </span>
            )}
          </div>
          {subtitle && <p className="text-sm text-muted-foreground">{subtitle}</p>}
          <div className="flex items-center gap-3 pt-2 text-xs text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <Clock className="h-3.5 w-3.5" />
              <span>{time}</span>
            </div>
            {duration && <span>• {duration}</span>}
          </div>
        </div>
      </div>
    </Card>
  );
};

export default PlanCard;
