import { Card } from "@/components/ui/card";
import { BookOpen, Brain, Heart, Calendar } from "lucide-react";

const QuickStatsCards = () => {
  const stats = [
    {
      icon: BookOpen,
      label: "Active Course",
      value: "CS228",
      subtext: "Next quiz in 2 days",
      color: "text-primary",
    },
    {
      icon: Brain,
      label: "Study Plan",
      value: "3 sessions",
      subtext: "Remaining this week",
      color: "text-accent",
    },
    {
      icon: Heart,
      label: "Wellness",
      value: "Focused",
      subtext: "Keep up the pace!",
      color: "text-success",
    },
    {
      icon: Calendar,
      label: "Upcoming",
      value: "Oct 17",
      subtext: "Linear Algebra exam",
      color: "text-primary",
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <Card key={stat.label} className="border-2 border-border p-4 shadow-card bg-card">
          <div className="flex items-start gap-3">
            <stat.icon className={`h-5 w-5 ${stat.color} mt-0.5`} />
            <div className="flex-1 min-w-0">
              <p className="text-xs text-muted-foreground mb-1">{stat.label}</p>
              <p className="text-lg font-bold text-foreground truncate">{stat.value}</p>
              <p className="text-xs text-muted-foreground">{stat.subtext}</p>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
};

export default QuickStatsCards;
