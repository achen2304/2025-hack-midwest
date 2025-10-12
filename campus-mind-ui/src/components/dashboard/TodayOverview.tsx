import { Card } from "@/components/ui/card";
import { Calendar, CheckCircle2, Heart } from "lucide-react";

interface TodayOverviewProps {
  userName: string;
  tasksDue: number;
  studyHours: number;
  wellnessScore: number;
}

const TodayOverview = ({ userName, tasksDue, studyHours, wellnessScore }: TodayOverviewProps) => {
  const today = new Date().toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
  });

  return (
    <Card className="border-2 border-border p-6 shadow-card bg-card">
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-foreground mb-1">
          Good morning, {userName}! 👋
        </h2>
        <p className="text-sm text-muted-foreground">{today}</p>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="flex flex-col items-center p-4 rounded-xl bg-primary/5 border-2 border-primary/20">
          <Calendar className="h-6 w-6 text-primary mb-2" />
          <span className="text-2xl font-bold text-foreground">{tasksDue}</span>
          <span className="text-xs text-muted-foreground">Tasks Due</span>
        </div>

        <div className="flex flex-col items-center p-4 rounded-xl bg-accent/5 border-2 border-accent/20">
          <CheckCircle2 className="h-6 w-6 text-accent mb-2" />
          <span className="text-2xl font-bold text-foreground">{studyHours}h</span>
          <span className="text-xs text-muted-foreground">Study Hours</span>
        </div>

        <div className="flex flex-col items-center p-4 rounded-xl bg-success/5 border-2 border-success/20">
          <Heart className="h-6 w-6 text-success mb-2" />
          <span className="text-2xl font-bold text-foreground">{wellnessScore}%</span>
          <span className="text-xs text-muted-foreground">Wellness</span>
        </div>
      </div>
    </Card>
  );
};

export default TodayOverview;
