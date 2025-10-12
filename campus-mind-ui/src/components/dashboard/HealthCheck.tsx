"use client"

import { Card } from "@/components/ui/card";
import { Heart } from "lucide-react";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";

const moods = [
  { emoji: "😄", label: "Great", value: 5 },
  { emoji: "🙂", label: "Good", value: 4 },
  { emoji: "😐", label: "Okay", value: 3 },
  { emoji: "😔", label: "Low", value: 2 },
  { emoji: "😫", label: "Stressed", value: 1 },
];

const HealthCheck = () => {
  const [selectedMood, setSelectedMood] = useState<number | null>(null);
  const { toast } = useToast();

  const handleMoodSelect = (value: number) => {
    setSelectedMood(value);
    const mood = moods.find((m) => m.value === value);
    
    if (value <= 2) {
      toast({
        title: "We've got you covered",
        description: "We'll adjust your schedule with lighter study blocks and more breaks today.",
      });
    } else {
      toast({
        title: "Great to hear!",
        description: `Glad you're feeling ${mood?.label.toLowerCase()}. Let's make the most of today!`,
      });
    }
  };

  return (
    <Card className="border-2 border-border p-6 shadow-card bg-card">
      <div className="flex items-center gap-2 mb-4">
        <Heart className="h-5 w-5 text-success" />
        <h3 className="text-base font-semibold text-foreground">Health Check</h3>
      </div>

      <p className="text-sm text-muted-foreground mb-4">How are you feeling today?</p>

      <div className="flex justify-center gap-2 mx-auto max-w-md">
        {moods.map((mood) => (
          <button
            key={mood.value}
            onClick={() => handleMoodSelect(mood.value)}
            title={mood.label}
            className={`flex items-center justify-center p-3 rounded-lg border-2 transition-all hover:scale-105 w-12 h-12 ${
              selectedMood === mood.value
                ? "border-primary bg-primary/10 shadow-glow"
                : "border-border hover:border-primary/50"
            }`}
          >
            <span className="text-2xl">{mood.emoji}</span>
          </button>
        ))}
      </div>

      {selectedMood && (
        <div className="mt-4 p-3 rounded-lg bg-success/10 border-2 border-success/30 animate-fade-in">
          <p className="text-xs text-center text-muted-foreground">
            Your wellness data helps our AI optimize your schedule for better balance
          </p>
        </div>
      )}
    </Card>
  );
};

export default HealthCheck;
