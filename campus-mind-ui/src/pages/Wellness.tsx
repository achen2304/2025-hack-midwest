"use client"

import { useState } from "react";
import { Heart, Wind, Activity, BookMarked, Sparkles, Flame } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import MoodChip from "@/components/MoodChip";
import { toast } from "sonner";
import ProgressCard from "@/components/ProgressCard";

const Wellness = () => {
  const [selectedMood, setSelectedMood] = useState("");
  const [duration, setDuration] = useState([30]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [routine, setRoutine] = useState<any>(null);

  const moods = [
    { id: "anxious", label: "Anxious", icon: Wind },
    { id: "tired", label: "Tired", icon: Activity },
    { id: "motivated", label: "Motivated", icon: Heart },
    { id: "calm", label: "Calm", icon: BookMarked },
  ];

  const handleGenerate = () => {
    if (!selectedMood) {
      toast.error("Please select your current mood");
      return;
    }

    setIsGenerating(true);

    setTimeout(() => {
      setRoutine({
        activities: [
          { icon: Wind, title: "Deep Breathing", description: "Box breathing: 4-4-4-4 pattern", duration: "5 min" },
          { icon: Activity, title: "Light Stretching", description: "Gentle neck and shoulder movements", duration: "5 min" },
          { icon: BookMarked, title: "Guided Meditation", description: "Body scan relaxation", duration: "10 min" },
          { icon: Heart, title: "Gratitude Journaling", description: "Write 3 things you're grateful for", duration: "10 min" },
        ],
      });
      setIsGenerating(false);
      toast.success("Wellness routine created!");
    }, 1500);
  };

  return (
    <div className="animate-fade-in space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Wellness Space</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Take a moment to check in with yourself 💙
          </p>
        </div>
      </div>

      {/* Wellness Progress */}
      <div className="grid gap-4 sm:grid-cols-2">
        <ProgressCard
          title="Weekly Wellness"
          value={5}
          total={7}
          icon={Heart}
          color="accent"
          message="5 days of self-care this week! 💪"
        />
        <Card className="border-border bg-gradient-to-br from-orange-500/5 to-red-500/5 p-6 shadow-card">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-orange-500/10">
              <Flame className="h-5 w-5 text-orange-500" />
            </div>
            <div>
              <div className="text-sm font-medium text-muted-foreground">Wellness Streak</div>
              <div className="text-2xl font-bold text-foreground mt-1">5 Days 🔥</div>
            </div>
          </div>
          <p className="text-xs text-muted-foreground italic mt-3">
            Complete today&apos;s routine to keep your streak!
          </p>
        </Card>
      </div>

      {/* Mood Selection */}
      <Card className="border-border bg-card p-6 shadow-card">
        <div className="space-y-6">
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-foreground">How are you feeling?</h3>
            <div className="flex flex-wrap gap-3">
              {moods.map((mood) => (
                <MoodChip
                  key={mood.id}
                  icon={mood.icon}
                  label={mood.label}
                  isActive={selectedMood === mood.id}
                  onClick={() => setSelectedMood(mood.id)}
                />
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-foreground">Available Time</h3>
              <span className="text-sm font-medium text-accent">{duration[0]} minutes</span>
            </div>
            <Slider
              value={duration}
              onValueChange={setDuration}
              min={15}
              max={60}
              step={5}
              className="py-4"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>15 min</span>
              <span>60 min</span>
            </div>
          </div>

          <Button
            onClick={handleGenerate}
            disabled={isGenerating}
            className="w-full gap-2 rounded-xl bg-gradient-to-r from-accent to-primary shadow-md transition-all duration-200 hover:shadow-lg"
          >
            {isGenerating ? (
              <>
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary-foreground border-t-transparent" />
                Creating Routine...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                Generate Wellness Routine
              </>
            )}
          </Button>
        </div>
      </Card>

      {/* Generated Routine */}
      {routine && (
        <div className="animate-slide-up space-y-4">
          <h2 className="flex items-center gap-2 text-xl font-semibold text-foreground">
            <Heart className="h-5 w-5 text-accent" />
            Your Personalized Routine
          </h2>

          <div className="grid gap-4 sm:grid-cols-2">
            {routine.activities.map((activity: any, index: number) => (
              <Card
                key={index}
                className="group overflow-hidden border-border bg-card shadow-card transition-all duration-300 hover:-translate-y-1 hover:shadow-card-hover"
              >
                <div className="flex items-start gap-4 p-5">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-accent/10">
                    <activity.icon className="h-6 w-6 text-accent" />
                  </div>
                  <div className="flex-1 space-y-1">
                    <h3 className="font-semibold text-foreground">{activity.title}</h3>
                    <p className="text-sm text-muted-foreground">{activity.description}</p>
                    <div className="pt-2 text-xs font-medium text-accent">{activity.duration}</div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Inspirational Quote */}
      <Card className="border-l-4 border-l-accent bg-gradient-to-r from-accent/5 to-primary/5 p-6 shadow-card">
        <div className="flex items-center justify-center gap-3">
          <span className="text-2xl">💙</span>
          <p className="text-center text-lg font-medium text-foreground">
            &ldquo;Small steps matter. Every moment you invest in yourself counts.&rdquo;
          </p>
        </div>
      </Card>
    </div>
  );
};

export default Wellness;
