import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Sparkles } from "lucide-react";

const AIRecommendations = () => {
  const recommendations = [
    {
      id: 1,
      text: "Review Algorithms chapter today",
      action: "Add to plan",
    },
    {
      id: 2,
      text: "Shift Physics study to tomorrow 6 PM",
      action: "Apply",
    },
    {
      id: 3,
      text: "Take a 15-min break after next session",
      action: "Remind me",
    },
  ];

  return (
    <Card className="border-2 border-border p-4 shadow-card bg-card">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="h-4 w-4 text-primary" />
        <h3 className="text-sm font-semibold text-foreground">CampusMind recommends</h3>
      </div>

      <div className="space-y-3">
        {recommendations.map((rec) => (
          <div key={rec.id} className="space-y-2">
            <p className="text-sm text-foreground">{rec.text}</p>
            <Button variant="outline" size="sm" className="w-full border-2">
              {rec.action}
            </Button>
          </div>
        ))}
      </div>
    </Card>
  );
};

export default AIRecommendations;
