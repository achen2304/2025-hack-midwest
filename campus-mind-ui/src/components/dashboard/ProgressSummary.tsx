import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Trophy, BookOpen, Heart, Target } from "lucide-react";

const ProgressSummary = () => {
  const goals = [
    { name: "Academic Goals", progress: 75, icon: BookOpen, color: "text-primary" },
    { name: "Wellness Goals", progress: 60, icon: Heart, color: "text-success" },
    { name: "Personal Goals", progress: 45, icon: Target, color: "text-accent" },
  ];

  return (
    <Card className="border-2 border-border p-6 shadow-card bg-card">
      <div className="flex items-center gap-2 mb-6">
        <Trophy className="h-5 w-5 text-primary" />
        <h3 className="text-lg font-semibold text-foreground">Weekly Progress</h3>
      </div>

      <div className="space-y-6">
        {goals.map((goal) => (
          <div key={goal.name} className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <goal.icon className={`h-4 w-4 ${goal.color}`} />
                <span className="text-sm font-medium text-foreground">{goal.name}</span>
              </div>
              <span className="text-sm font-semibold text-foreground">{goal.progress}%</span>
            </div>
            <Progress value={goal.progress} className="h-2" />
          </div>
        ))}

        <div className="pt-4 mt-4 border-t-2 border-border">
          <div className="flex items-center justify-between p-3 rounded-lg bg-primary/5">
            <span className="text-sm font-medium text-foreground">Overall Completion</span>
            <span className="text-xl font-bold text-primary">60%</span>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default ProgressSummary;
