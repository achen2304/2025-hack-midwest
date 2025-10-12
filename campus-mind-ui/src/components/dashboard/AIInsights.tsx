import { Card } from "@/components/ui/card";
import { Brain, Sparkles } from "lucide-react";

const AIInsights = () => {
  const insights = [
    {
      agent: "Schedule Maker",
      message: "You have a 3-hour gap tomorrow afternoon. Perfect for your Math 241 review!",
      icon: "📅",
    },
    {
      agent: "Study Planner",
      message:
        "Based on your past performance, consider breaking your CS assignment into two 45-minute sessions.",
      icon: "📘",
    },
    {
      agent: "Wellness Check",
      message: "You've been studying for 2 hours. Time for a 15-minute stretch break!",
      icon: "❤️",
    },
  ];

  return (
    <Card className="border-2 border-border p-6 shadow-card bg-gradient-to-br from-primary/5 to-accent/5">
      <div className="flex items-center gap-2 mb-4">
        <Brain className="h-5 w-5 text-primary" />
        <h3 className="text-base font-semibold text-foreground">AI Insights</h3>
      </div>

      <div className="space-y-3">
        {insights.map((insight, index) => (
          <div
            key={index}
            className="p-4 rounded-xl bg-card border-2 border-border hover:border-primary/50 transition-colors"
          >
            <div className="flex items-start gap-3">
              <span className="text-2xl">{insight.icon}</span>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <Sparkles className="h-3 w-3 text-accent" />
                  <span className="text-xs font-semibold text-accent">{insight.agent}</span>
                </div>
                <p className="text-sm text-muted-foreground">{insight.message}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 p-3 rounded-lg bg-accent/10 border-2 border-accent/30">
        <p className="text-xs text-center text-muted-foreground">
          <span className="font-semibold text-foreground">Vector Agent</span> is learning your
          study patterns to provide better recommendations
        </p>
      </div>
    </Card>
  );
};

export default AIInsights;
