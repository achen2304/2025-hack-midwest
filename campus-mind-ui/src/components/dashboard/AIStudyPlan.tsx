"use client"

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Brain, Clock, BookOpen, RefreshCw } from "lucide-react";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";

const AIStudyPlan = () => {
  const { toast } = useToast();
  const [isGenerating, setIsGenerating] = useState(false);

  const handleRegenerate = () => {
    setIsGenerating(true);
    setTimeout(() => {
      setIsGenerating(false);
      toast({
        title: "Plan Updated!",
        description: "Your study plan has been optimized based on your current schedule.",
      });
    }, 1500);
  };

  return (
    <Card className="border-2 border-border p-6 shadow-card bg-gradient-to-br from-primary/5 to-accent/5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Brain className="h-5 w-5 text-primary" />
          <h3 className="text-lg font-semibold text-foreground">AI Study Plan</h3>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleRegenerate}
          disabled={isGenerating}
          className="gap-2"
        >
          <RefreshCw className={`h-4 w-4 ${isGenerating ? "animate-spin" : ""}`} />
          {isGenerating ? "Generating..." : "Regenerate"}
        </Button>
      </div>

      <div className="space-y-4">
        <div className="flex items-start gap-4 p-4 rounded-xl bg-card border-2 border-primary/30">
          <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
            <Clock className="h-6 w-6 text-primary" />
          </div>
          <div className="flex-1">
            <h4 className="font-semibold text-foreground mb-1">Next Study Block</h4>
            <p className="text-sm text-muted-foreground mb-2">10:00 AM - 11:30 AM</p>
            <div className="flex items-center gap-2 text-sm">
              <BookOpen className="h-4 w-4 text-accent" />
              <span className="font-medium text-foreground">Data Structures Review</span>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Focus on Binary Trees & Graph Algorithms
            </p>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-accent/10 border-2 border-accent/30">
          <p className="text-sm text-muted-foreground">
            <span className="font-semibold text-foreground">AI Recommendation:</span> You have a
            3-hour gap after lunch. Perfect for tackling your Calculus problem set while your
            energy is high.
          </p>
        </div>
      </div>
    </Card>
  );
};

export default AIStudyPlan;
