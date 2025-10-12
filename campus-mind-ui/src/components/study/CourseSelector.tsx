import { GraduationCap, Link2 } from "lucide-react";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface CourseSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

const courses = [
  { id: "math241", name: "MATH 241: Linear Algebra", color: "#3B82F6" },
  { id: "bio202", name: "BIO 202: Human Anatomy", color: "#10B981" },
  { id: "psych101", name: "PSYCH 101: Introduction to Psychology", color: "#8B5CF6" },
  { id: "cs201", name: "CS 201: Data Structures", color: "#F59E0B" },
  { id: "chem110", name: "CHEM 110: General Chemistry", color: "#EF4444" },
];

const CourseSelector = ({ value, onChange }: CourseSelectorProps) => {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <GraduationCap className="h-5 w-5 text-primary" />
        <Label className="text-base font-semibold">Step 1: Select a Course</Label>
      </div>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger className="rounded-lg">
          <SelectValue placeholder="Choose your course" />
        </SelectTrigger>
        <SelectContent>
          {courses.map((course) => (
            <SelectItem key={course.id} value={course.id}>
              <div className="flex items-center gap-2">
                <div
                  className="h-2 w-2 rounded-full"
                  style={{ backgroundColor: course.color }}
                />
                {course.name}
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <p className="text-xs text-muted-foreground flex items-center gap-1">
        <Link2 className="h-3 w-3" />
        Courses synced from Canvas automatically
      </p>
    </div>
  );
};

export default CourseSelector;
