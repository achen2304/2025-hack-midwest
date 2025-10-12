"use client"

import { useState } from "react";
import { Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";
import StudyPlannerHeader from "@/components/study/StudyPlannerHeader";
import CourseSelector from "@/components/study/CourseSelector";
import TopicSelector from "@/components/study/TopicSelector";
import ResourceUploader from "@/components/study/ResourceUploader";
import StudyPlanResults from "@/components/study/StudyPlanResults";
import AITutorPanel from "@/components/study/AITutorPanel";
import ProgressWidget from "@/components/study/ProgressWidget";

const Study = () => {
  const [course, setCourse] = useState("");
  const [topic, setTopic] = useState("");
  const [purpose, setPurpose] = useState("exam");
  const [selectedExam, setSelectedExam] = useState("");
  const [notes, setNotes] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedPlan, setGeneratedPlan] = useState(false);

  const handleGenerate = async () => {
    if (!course || !topic) {
      toast.error("Please select a course and enter a topic");
      return;
    }

    setIsGenerating(true);
    
    setTimeout(() => {
      setGeneratedPlan(true);
      setIsGenerating(false);
      toast.success("Study plan generated successfully!");
    }, 2000);
  };

  return (
    <div className="animate-fade-in">
      <StudyPlannerHeader />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {!generatedPlan ? (
            <>
              <Card className="border-border bg-card p-6 shadow-card">
                <CourseSelector value={course} onChange={setCourse} />
              </Card>

              <Card className="border-border bg-card p-6 shadow-card">
                <TopicSelector
                  course={course}
                  topic={topic}
                  onTopicChange={setTopic}
                  purpose={purpose}
                  onPurposeChange={setPurpose}
                  selectedExam={selectedExam}
                  onExamChange={setSelectedExam}
                />
              </Card>

              <Card className="border-border bg-card p-6 shadow-card">
                <ResourceUploader notes={notes} onNotesChange={setNotes} />
              </Card>

              <Button
                onClick={handleGenerate}
                disabled={isGenerating}
                size="lg"
                className="w-full gap-2 rounded-xl gradient-primary shadow-glow hover:shadow-glow-accent"
              >
                {isGenerating ? (
                  <>
                    <div className="h-5 w-5 animate-spin rounded-full border-2 border-primary-foreground border-t-transparent" />
                    Generating Your Study Plan...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-5 w-5" />
                    Generate My Study Plan
                  </>
                )}
              </Button>
            </>
          ) : (
            <StudyPlanResults />
          )}
        </div>

        <div className="space-y-6">
          {generatedPlan ? (
            <>
              <ProgressWidget />
              <AITutorPanel />
            </>
          ) : (
            <Card className="border-border bg-gradient-to-br from-primary/5 to-accent/5 p-6 shadow-card sticky top-6">
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-primary" />
                  <h3 className="font-semibold text-foreground">What to Expect</h3>
                </div>
                <ul className="space-y-3 text-sm text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-0.5">📚</span>
                    <span>AI-powered study plan tailored to your exam date</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-0.5">📅</span>
                    <span>Daily breakdown with time estimates and resources</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-0.5">💬</span>
                    <span>Interactive AI tutor for questions and explanations</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-0.5">📊</span>
                    <span>Progress tracking with XP rewards and streaks</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-0.5">🔄</span>
                    <span>Flexible plan adjustments based on your pace</span>
                  </li>
                </ul>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default Study;
