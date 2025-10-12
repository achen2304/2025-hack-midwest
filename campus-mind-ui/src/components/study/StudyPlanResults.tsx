import { Clock, CheckCircle2, MessageCircle, RefreshCw, TrendingUp } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

interface StudyDay {
  day: number;
  title: string;
  topics: string;
  duration: string;
  resources: string[];
  completed: boolean;
}

const studyDays: StudyDay[] = [
  {
    day: 1,
    title: "Matrix Multiplication & Inverse",
    topics: "Introduction to matrix operations",
    duration: "1.5 hrs",
    resources: ["Lecture 7 slides", "Notes: Section 4.2"],
    completed: true,
  },
  {
    day: 2,
    title: "Determinants & Properties",
    topics: "Understanding determinant calculations",
    duration: "2 hrs",
    resources: ["Chapter 5", "Practice problems 1-15"],
    completed: true,
  },
  {
    day: 3,
    title: "Eigenvalues & Eigenvectors",
    topics: "Core concepts and applications",
    duration: "2.5 hrs",
    resources: ["Lecture 9 slides", "Video tutorial"],
    completed: false,
  },
  {
    day: 4,
    title: "Practice Problems & Review",
    topics: "Mixed problem sets",
    duration: "2 hrs",
    resources: ["Practice exam", "Online quiz"],
    completed: false,
  },
  {
    day: 5,
    title: "Final Review & Mock Test",
    topics: "Comprehensive review session",
    duration: "3 hrs",
    resources: ["Mock midterm", "Summary notes"],
    completed: false,
  },
];

const StudyPlanResults = () => {
  const completedDays = studyDays.filter((day) => day.completed).length;
  const progressPercent = (completedDays / studyDays.length) * 100;

  return (
    <div className="space-y-4 animate-slide-up">
      <div className="flex items-center gap-2">
        <TrendingUp className="h-5 w-5 text-success" />
        <h2 className="text-xl font-semibold text-foreground">Your AI-Generated Study Plan</h2>
      </div>

      <Card className="border-border bg-primary/5 p-5 shadow-card">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="font-semibold text-foreground">5-Day Prep Plan</h3>
            <p className="text-sm text-muted-foreground mt-1">
              Midterm 2: Linear Algebra • March 15, 2025
            </p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-primary">{completedDays}/5</p>
            <p className="text-xs text-muted-foreground">sessions complete</p>
          </div>
        </div>
        <Progress value={progressPercent} className="mt-4 h-2" />
      </Card>

      <div className="space-y-3">
        {studyDays.map((day) => (
          <Card
            key={day.day}
            className={`p-4 border-border shadow-card transition-all duration-200 hover:-translate-y-0.5 hover:shadow-card-hover ${
              day.completed ? "bg-success/5 border-success/20" : "bg-card"
            }`}
          >
            <div className="flex items-start gap-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary flex-shrink-0">
                {day.day}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <h4 className="font-medium text-foreground">{day.title}</h4>
                    <p className="text-sm text-muted-foreground mt-1">{day.topics}</p>
                    <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {day.duration}
                      </span>
                      <span>📚 {day.resources.join(" • ")}</span>
                    </div>
                  </div>
                  {day.completed && (
                    <CheckCircle2 className="h-5 w-5 text-success flex-shrink-0" />
                  )}
                </div>
                <div className="flex gap-2 mt-3">
                  <Button
                    size="sm"
                    variant={day.completed ? "outline" : "default"}
                    className="gap-1.5"
                  >
                    <CheckCircle2 className="h-3.5 w-3.5" />
                    {day.completed ? "Completed" : "Mark Complete"}
                  </Button>
                  <Button size="sm" variant="outline" className="gap-1.5">
                    <MessageCircle className="h-3.5 w-3.5" />
                    Ask Tutor
                  </Button>
                  <Button size="sm" variant="ghost" className="gap-1.5">
                    <RefreshCw className="h-3.5 w-3.5" />
                    Regenerate
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default StudyPlanResults;
