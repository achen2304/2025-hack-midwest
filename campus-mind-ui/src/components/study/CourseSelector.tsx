'use client';

import { useEffect, useMemo, useState } from "react";
import { GraduationCap, Link2 } from "lucide-react";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";

interface CourseSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

type Course = {
  id: string | number;
  name: string;
  course_code?: string;
  enrollment_term_id?: number;
  start_at?: string | null;
  end_at?: string | null;
};

// quick deterministic color from id (stable across renders)
function colorFor(id: string | number) {
  const s = String(id);
  let hash = 0;
  for (let i = 0; i < s.length; i++) hash = (hash * 31 + s.charCodeAt(i)) | 0;
  const hue = Math.abs(hash) % 360;
  return `hsl(${hue} 70% 45%)`;
}

export default function CourseSelector({ value, onChange }: CourseSelectorProps) {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        setLoading(true);
        setErr(null);
        const res = await fetch("/api/backend/canvas/courses", {
          // same-origin; cookies auto-sent to your proxy route
          method: "GET",
          headers: { "accept": "application/json" },
        });
        if (!res.ok) {
          throw new Error(`Failed to load courses (${res.status})`);
        }
        const data: Course[] = await res.json();

        // sort: put current/future/active courses first, then by name
        const now = Date.now();
        const filtered = data.filter(
          (c) => !c.name?.toLowerCase().includes("done")
        );

        const sorted = [...filtered].sort((a, b) => {
          const aActive =
            !a.end_at || new Date(a.end_at).getTime() >= now ? 1 : 0;
          const bActive =
            !b.end_at || new Date(b.end_at).getTime() >= now ? 1 : 0;
          if (aActive !== bActive) return bActive - aActive;
          return (a.name || "").localeCompare(b.name || "");
        });

        if (mounted) setCourses(sorted);
      } catch (e: any) {
        if (mounted) setErr(e?.message ?? "Failed to load courses");
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  const options = useMemo(
    () =>
      courses.map((c) => ({
        id: String(c.id),
        name: c.name || c.course_code || String(c.id),
        color: colorFor(c.id),
      })),
    [courses]
  );

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <GraduationCap className="h-5 w-5 text-primary" />
        <Label className="text-base font-semibold">Step 1: Select a Course</Label>
      </div>

      {loading ? (
        <div className="space-y-2">
          <Skeleton className="h-10 w-full rounded-lg" />
          <p className="text-xs text-muted-foreground">Loading courses…</p>
        </div>
      ) : err ? (
        <div className="text-sm text-destructive">
          {err}
        </div>
      ) : options.length === 0 ? (
        <div className="text-sm text-muted-foreground">
          No courses found.
        </div>
      ) : (
        <Select value={value} onValueChange={onChange}>
          <SelectTrigger className="rounded-lg">
            <SelectValue placeholder="Choose your course" />
          </SelectTrigger>
          <SelectContent>
            {options.map((course) => (
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
      )}

      <p className="text-xs text-muted-foreground flex items-center gap-1">
        <Link2 className="h-3 w-3" />
        Courses synced from Canvas automatically
      </p>
    </div>
  );
}
