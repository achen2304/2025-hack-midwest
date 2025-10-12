"use client"

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Clock, Edit, CheckCircle, Plus, Calendar } from "lucide-react";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";

interface StudyBlock {
  id: number;
  time: string;
  title: string;
  duration: string;
}

const TodayStudyPlan = () => {
  const { toast } = useToast();
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [blocks, setBlocks] = useState<StudyBlock[]>([
    { id: 1, time: "9:00 AM", title: "Data Structures - Trees", duration: "45 min" },
    { id: 2, time: "2:00 PM", title: "Linear Algebra Review", duration: "60 min" },
    { id: 3, time: "5:00 PM", title: "Physics - Thermodynamics", duration: "45 min" },
  ]);

  const handleRegenerate = () => {
    setIsRegenerating(true);
    setTimeout(() => {
      setIsRegenerating(false);
      toast({
        title: "Study plan regenerated",
        description: "Your schedule has been optimized with AI",
      });
    }, 1500);
  };

  return (
    <Card className="border-2 border-border p-6 shadow-card bg-card">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-foreground">Today&apos;s Study Plan</h3>
          <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
            <Calendar className="h-3 w-3" />
            Auto-scheduled via Google Calendar sync
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleRegenerate}
          disabled={isRegenerating}
          className="border-2"
        >
          {isRegenerating ? "Regenerating..." : "Regenerate with AI"}
        </Button>
      </div>

      <div className="space-y-3">
        {blocks.map((block) => (
          <div
            key={block.id}
            className="flex items-center gap-3 p-4 rounded-lg border-2 border-border bg-card hover:bg-muted/50 transition-colors"
          >
            <Clock className="h-4 w-4 text-muted-foreground flex-shrink-0" />
            <span className="text-sm font-semibold text-foreground w-20 flex-shrink-0">
              {block.time}
            </span>
            <div className="flex-1">
              <p className="text-sm font-medium text-foreground">{block.title}</p>
              <p className="text-xs text-muted-foreground">{block.duration}</p>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <Edit className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <CheckCircle className="h-4 w-4" />
              </Button>
            </div>
          </div>
        ))}

        <Button variant="outline" className="w-full border-2" size="lg">
          <Plus className="h-4 w-4 mr-2" />
          Add study block
        </Button>
      </div>
    </Card>
  );
};

export default TodayStudyPlan;
