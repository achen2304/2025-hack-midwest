import { BookOpen, Calendar } from "lucide-react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface TopicSelectorProps {
  course: string;
  topic: string;
  onTopicChange: (value: string) => void;
  purpose: string;
  onPurposeChange: (value: string) => void;
  selectedExam: string;
  onExamChange: (value: string) => void;
}

// Mock Canvas exam data - would come from Canvas API
const canvasExams: Record<string, Array<{ id: string; title: string; type: string; date: string }>> = {
  math241: [
    { id: "exam1", title: "Midterm 1: Vectors & Linear Systems", type: "exam", date: "March 10, 2025" },
    { id: "exam2", title: "Midterm 2: Matrix Operations", type: "exam", date: "March 15, 2025" },
    { id: "quiz1", title: "Quiz 4: Eigenvalues", type: "quiz", date: "March 8, 2025" },
    { id: "final", title: "Final Exam", type: "exam", date: "April 20, 2025" },
  ],
  bio202: [
    { id: "exam1", title: "Exam 1: Cell Structure", type: "exam", date: "March 12, 2025" },
    { id: "quiz1", title: "Quiz 3: Nervous System", type: "quiz", date: "March 9, 2025" },
    { id: "exam2", title: "Exam 2: Organ Systems", type: "exam", date: "March 25, 2025" },
  ],
  psych101: [
    { id: "exam1", title: "Midterm: Cognitive Psychology", type: "exam", date: "March 14, 2025" },
    { id: "quiz1", title: "Quiz 5: Memory & Learning", type: "quiz", date: "March 11, 2025" },
  ],
  cs201: [
    { id: "exam1", title: "Midterm: Trees & Graphs", type: "exam", date: "March 16, 2025" },
    { id: "quiz1", title: "Quiz 3: Hash Tables", type: "quiz", date: "March 10, 2025" },
  ],
  chem110: [
    { id: "exam1", title: "Exam 2: Chemical Bonding", type: "exam", date: "March 13, 2025" },
    { id: "quiz1", title: "Quiz 4: Stoichiometry", type: "quiz", date: "March 9, 2025" },
  ],
};

const TopicSelector = ({
  course,
  topic,
  onTopicChange,
  purpose,
  onPurposeChange,
  selectedExam,
  onExamChange,
}: TopicSelectorProps) => {
  const availableExams = course ? canvasExams[course] || [] : [];
  const selectedExamData = availableExams.find(exam => exam.id === selectedExam);

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <BookOpen className="h-5 w-5 text-primary" />
        <Label className="text-base font-semibold">Step 2: Choose Topic or Unit</Label>
      </div>
      
      <div className="space-y-2">
        <Input
          placeholder="e.g., Vectors and Matrices, Photosynthesis, Statistical Inference"
          value={topic}
          onChange={(e) => onTopicChange(e.target.value)}
          className="rounded-lg"
        />
      </div>

      {course && availableExams.length > 0 && (
        <div className="space-y-2">
          <Label className="text-sm flex items-center gap-1.5">
            <Calendar className="h-3.5 w-3.5" />
            Select Upcoming Exam/Quiz from Canvas
          </Label>
          <Select value={selectedExam} onValueChange={onExamChange}>
            <SelectTrigger className="rounded-lg">
              <SelectValue placeholder="Choose an exam or quiz" />
            </SelectTrigger>
            <SelectContent>
              {availableExams.map((exam) => (
                <SelectItem key={exam.id} value={exam.id}>
                  <div className="flex items-center gap-2">
                    <span className={`px-1.5 py-0.5 text-xs rounded ${
                      exam.type === 'exam' ? 'bg-primary/10 text-primary' : 'bg-accent/10 text-accent'
                    }`}>
                      {exam.type.toUpperCase()}
                    </span>
                    <span>{exam.title}</span>
                    <span className="text-muted-foreground">• {exam.date}</span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {selectedExamData && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground bg-accent/5 border border-border rounded-lg p-2.5">
              <Calendar className="h-3.5 w-3.5" />
              <span>Scheduled for <span className="font-medium text-foreground">{selectedExamData.date}</span></span>
            </div>
          )}
          <p className="text-xs text-muted-foreground flex items-center gap-1">
            <span className="h-1.5 w-1.5 rounded-full bg-success animate-pulse" />
            Synced from Canvas automatically
          </p>
        </div>
      )}

      {!course && (
        <div className="text-sm text-muted-foreground bg-muted/30 border border-border rounded-lg p-3">
          Select a course first to see upcoming exams and quizzes from Canvas
        </div>
      )}
    </div>
  );
};

export default TopicSelector;
