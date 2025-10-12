import { Calendar, Edit, RefreshCw } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

const ProgressWidget = () => {
  return (
    <Card className="border-border bg-card p-5 shadow-card sticky top-6">
      <div className="space-y-4">
        <div className="text-center">
          <div className="relative inline-flex items-center justify-center w-24 h-24 mb-3">
            <svg className="w-24 h-24 transform -rotate-90">
              <circle
                cx="48"
                cy="48"
                r="44"
                stroke="currentColor"
                strokeWidth="8"
                fill="transparent"
                className="text-muted"
              />
              <circle
                cx="48"
                cy="48"
                r="44"
                stroke="currentColor"
                strokeWidth="8"
                fill="transparent"
                strokeDasharray={276.46}
                strokeDashoffset={110.58}
                className="text-primary"
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-2xl font-bold text-foreground">60%</span>
            </div>
          </div>
          <p className="text-sm font-medium text-foreground">3/5 Sessions Complete</p>
          <p className="text-xs text-muted-foreground mt-1">Keep up the great work!</p>
        </div>

        <div className="pt-4 border-t border-border space-y-3">
          <div className="flex items-start gap-2">
            <Calendar className="h-4 w-4 text-primary mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-medium text-foreground">Next Study Session</p>
              <p className="text-xs text-muted-foreground">Tomorrow at 6:00 PM</p>
            </div>
          </div>

          <div className="space-y-2">
            <Button className="w-full gap-2" size="sm">
              <Calendar className="h-4 w-4" />
              Add to Calendar
            </Button>
            <Button variant="outline" className="w-full gap-2" size="sm">
              <Edit className="h-4 w-4" />
              Edit Plan
            </Button>
            <Button variant="outline" className="w-full gap-2" size="sm">
              <RefreshCw className="h-4 w-4" />
              Regenerate Plan
            </Button>
          </div>
        </div>

        <div className="pt-4 border-t border-border">
          <div className="flex items-center justify-between text-xs mb-2">
            <span className="text-muted-foreground">Days until exam</span>
            <span className="font-semibold text-foreground">3 days</span>
          </div>
          <Progress value={40} className="h-1.5" />
        </div>
      </div>
    </Card>
  );
};

export default ProgressWidget;
