'use client'

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Calendar, ExternalLink, CheckCircle2, ArrowRight, Brain } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useRouter } from "next/navigation";

type Course = {
  id: string;
  name: string;
  course_code?: string;
  is_tracked?: boolean;
};

export default function Onboarding() {
  const { toast } = useToast();
  const router = useRouter();

  // Canvas connect state
  const [canvasUrl, setCanvasUrl] = useState("");
  const [canvasToken, setCanvasToken] = useState("");
  const [canvasConnected, setCanvasConnected] = useState(false);

  // Google (still simulated)
  const [googleConnected, setGoogleConnected] = useState(false);

  // Courses + selection
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourseIds, setSelectedCourseIds] = useState<string[]>([]);

  // Loading flags
  const [savingToken, setSavingToken] = useState(false);
  const [loadingCourses, setLoadingCourses] = useState(false);
  const [syncing, setSyncing] = useState(false);

  // UI helpers
  const [disableContinue, setDisableContinue] = useState(true);

  // When we have selected courses, enable the final Sync & Continue button
  useEffect(() => {
    setDisableContinue(!(canvasConnected && selectedCourseIds.length > 0));
  }, [canvasConnected, selectedCourseIds]);

  const api = {
    saveToken: async (baseUrl: string, token: string) => {
      const res = await fetch('/api/backend/canvas/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ canvas_token: token, canvas_base_url: baseUrl }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || 'Failed to save Canvas token');
      }
    },
    fetchCourses: async (): Promise<Course[]> => {
      const res = await fetch('/api/backend/canvas/courses');
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || 'Failed to fetch courses');
      }
      return res.json();
    },
    trackCourses: async (courseIds: string[]) => {
      const res = await fetch('/api/backend/canvas/courses/track', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ course_ids: courseIds }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || 'Failed to save tracked courses');
      }
    },
    syncAll: async () => {
      const res = await fetch('/api/backend/canvas/sync', { method: 'POST' });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || 'Failed to sync Canvas data');
      }
    },
  };

  const handleCanvasConnect = async () => {
    if (!canvasUrl || !canvasToken) {
      toast({
        title: "Missing information",
        description: "Please enter both Canvas URL and access token.",
        variant: "destructive",
      });
      return;
    }

    try {
      setSavingToken(true);
      await api.saveToken(canvasUrl.trim(), canvasToken.trim());
      setCanvasConnected(true);
      setCanvasToken("");

      toast({ title: "Canvas connected! ✅", description: "Fetching your courses..." });

      // Immediately fetch courses after successful token save
      setLoadingCourses(true);
      const data = await api.fetchCourses();
      setCourses(data);

      // Pre-select any already-tracked courses
      const pre = data.filter((c) => c.is_tracked).map((c) => c.id);
      setSelectedCourseIds(pre);

      toast({
        title: "Courses loaded",
        description: `Found ${data.length} course${data.length === 1 ? '' : 's'}. Select which to track.`,
      });
    } catch (err: any) {
      toast({ title: "Canvas connection failed", description: err.message, variant: "destructive" });
    } finally {
      setSavingToken(false);
      setLoadingCourses(false);
    }
  };

  const toggleCourseSelection = (courseId: string) => {
    setSelectedCourseIds((prev) =>
      prev.includes(courseId) ? prev.filter((id) => id !== courseId) : [...prev, courseId]
    );
  };

  // Final step: save selected courses → sync assignments → go to dashboard
  const handleSyncAndContinue = async () => {
    if (!canvasConnected || selectedCourseIds.length === 0) {
      toast({
        title: "Select courses",
        description: "Please connect Canvas and choose at least one course.",
        variant: "destructive",
      });
      return;
    }

    try {
      setSyncing(true);
      await api.trackCourses(selectedCourseIds);
      // Sync pulls assignments for ONLY tracked courses (per your backend’s logic)
      await api.syncAll();

      toast({ title: "All set! 🎉", description: "Courses and assignments synced." });
      router.push("/dashboard");
    } catch (err: any) {
      toast({ title: "Sync failed", description: err.message, variant: "destructive" });
    } finally {
      setSyncing(false);
    }
  };

  // Simulated Google connect (unchanged)
  const handleGoogleConnect = () => {
    setGoogleConnected(true);
    toast({
      title: "Google Calendar connected! ✅",
      description: "Your events will appear in your schedule.",
    });
  };

  const handleSkip = () => router.push("/dashboard");

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl animate-fade-in">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="relative">
              <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full" />
              <Brain className="h-12 w-12 text-primary relative animate-float" />
            </div>
          </div>
          <h1 className="text-3xl font-bold mb-2">Welcome to CampusMind! 🎉</h1>
          <p className="text-muted-foreground">Let’s connect and import what you need</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-6">
          {/* Canvas Connection + Course Selection */}
          <Card className={canvasConnected ? "border-primary shadow-glow" : ""}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <div className="h-10 w-10 rounded-lg gradient-primary flex items-center justify-center">
                    <ExternalLink className="h-5 w-5 text-primary-foreground" />
                  </div>
                  Canvas LMS
                </CardTitle>
                {canvasConnected && <CheckCircle2 className="h-5 w-5 text-primary" />}
              </div>
              <CardDescription>Sync your courses and assignments into CampusMind</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {!canvasConnected ? (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="canvas-url">Canvas URL</Label>
                    <Input
                      id="canvas-url"
                      placeholder="https://your-school.instructure.com"
                      value={canvasUrl}
                      onChange={(e) => setCanvasUrl(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="canvas-token">Access Token</Label>
                    <Input
                      id="canvas-token"
                      type="password"
                      placeholder="Enter your Canvas API token"
                      value={canvasToken}
                      onChange={(e) => setCanvasToken(e.target.value)}
                    />
                  </div>
                  <div className="bg-muted/50 rounded-lg p-3 text-xs space-y-1">
                    <p className="font-medium">How to get your Canvas token:</p>
                    <ol className="list-decimal list-inside space-y-1 text-muted-foreground">
                      <li>Log into your Canvas account</li>
                      <li>Go to Account → Settings</li>
                      <li>Scroll to “Approved Integrations”</li>
                      <li>Click “+ New Access Token”</li>
                      <li>Paste the token here</li>
                    </ol>
                  </div>
                  <Button onClick={handleCanvasConnect} className="w-full" disabled={savingToken}>
                    {savingToken ? "Connecting..." : "Connect & Load Courses"}
                  </Button>
                </>
              ) : (
                <>
                  <div className="text-center py-3">
                    <p className="font-medium">Canvas Connected</p>
                    <p className="text-sm text-muted-foreground">
                      {loadingCourses ? "Loading courses..." : "Select courses to track"}
                    </p>
                  </div>

                  {courses.length > 0 && (
                    <div className="p-3 bg-muted/40 rounded-md max-h-64 overflow-y-auto">
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-sm font-medium">
                          Courses ({courses.length})
                        </p>
                        <div className="space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setSelectedCourseIds(courses.map((c) => c.id))}
                          >
                            Select all
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setSelectedCourseIds([])}
                          >
                            Clear
                          </Button>
                        </div>
                      </div>

                      <div className="space-y-2">
                        {courses.map((course) => {
                          const checked = selectedCourseIds.includes(course.id);
                          return (
                            <label
                              key={course.id}
                              className={`flex items-start gap-2 p-2 rounded border bg-white cursor-pointer hover:bg-gray-50 ${
                                checked ? "border-blue-500 bg-blue-50" : ""
                              }`}
                              onClick={() => toggleCourseSelection(course.id)}
                            >
                              <input
                                type="checkbox"
                                className="mt-1"
                                checked={checked}
                                onChange={() => toggleCourseSelection(course.id)}
                                onClick={(e) => e.stopPropagation()}
                              />
                              <div className="flex-1">
                                <p className="font-medium">{course.name}</p>
                                <p className="text-xs text-gray-600">{course.course_code}</p>
                                {course.is_tracked && (
                                  <span className="inline-block mt-1 px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded">
                                    Previously tracked
                                  </span>
                                )}
                              </div>
                            </label>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </>
              )}
            </CardContent>
          </Card>

          {/* Google Calendar (unchanged, optional) */}
          <Card className={googleConnected ? "border-primary shadow-glow" : ""}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <div className="h-10 w-10 rounded-lg gradient-primary flex items-center justify-center">
                    <Calendar className="h-5 w-5 text-primary-foreground" />
                  </div>
                  Google Calendar
                </CardTitle>
                {googleConnected && <CheckCircle2 className="h-5 w-5 text-primary" />}
              </div>
              <CardDescription>Import your schedule automatically</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {!googleConnected ? (
                <>
                  <div className="bg-muted/50 rounded-lg p-3 text-xs space-y-1">
                    <p className="font-medium">What you’ll get:</p>
                    <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                      <li>Class events in one place</li>
                      <li>Smart scheduling</li>
                      <li>Never miss a deadline</li>
                    </ul>
                  </div>
                  <Button onClick={handleGoogleConnect} variant="outline" className="w-full">
                    Connect Google Calendar
                  </Button>
                </>
              ) : (
                <div className="text-center py-6">
                  <CheckCircle2 className="h-12 w-12 text-primary mx-auto mb-2" />
                  <p className="font-medium">Google Calendar Connected</p>
                  <p className="text-sm text-muted-foreground">Events are syncing</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="flex items-center justify-between gap-4">
          <Button variant="ghost" onClick={handleSkip}>
            Skip for now
          </Button>

          <Button
            size="lg"
            onClick={handleSyncAndContinue}
            disabled={disableContinue || syncing}
          >
            {syncing ? "Syncing..." : "Sync Selected & Continue"}
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>

        <p className="text-center text-xs text-muted-foreground mt-6">
          You can always connect these later in Settings
        </p>
      </div>
    </div>
  );
}
