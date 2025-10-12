"use client"

import { useState } from "react";
import { Link2, CheckCircle2, AlertCircle, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

const ConnectCanvas = () => {
  const [step, setStep] = useState(1);
  const [canvasUrl, setCanvasUrl] = useState("");
  const [accessToken, setAccessToken] = useState("");
  const [isConnecting, setIsConnecting] = useState(false);
  const [syncedCourses, setSyncedCourses] = useState<any[]>([]);

  const handleConnect = async () => {
    if (!canvasUrl || !accessToken) {
      toast.error("Please fill in all fields");
      return;
    }

    setIsConnecting(true);

    setTimeout(() => {
      setSyncedCourses([
        { id: 1, name: "CS 101 - Data Structures", assignments: 5 },
        { id: 2, name: "MATH 201 - Calculus II", assignments: 3 },
        { id: 3, name: "PHYS 150 - Mechanics", assignments: 4 },
      ]);
      setIsConnecting(false);
      setStep(3);
      toast.success("Successfully connected to Canvas!");
    }, 2000);
  };

  return (
    <div className="animate-fade-in space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Connect Canvas</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Sync your courses and assignments from Canvas LMS
        </p>
      </div>

      {/* Progress Steps */}
      <div className="flex items-center justify-center gap-2">
        {[1, 2, 3].map((s) => (
          <div key={s} className="flex items-center">
            <div
              className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-semibold transition-all ${
                step >= s
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "bg-muted text-muted-foreground"
              }`}
            >
              {step > s ? <CheckCircle2 className="h-4 w-4" /> : s}
            </div>
            {s < 3 && (
              <div
                className={`h-0.5 w-12 transition-all ${
                  step > s ? "bg-primary" : "bg-muted"
                }`}
              />
            )}
          </div>
        ))}
      </div>

      {/* Step 1: Credentials */}
      {step === 1 && (
        <Card className="border-border bg-card p-6 shadow-card">
          <div className="space-y-6">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
                <Link2 className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground">Canvas Credentials</h3>
                <p className="text-sm text-muted-foreground">Enter your Canvas URL and access token</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="canvas-url">Canvas URL</Label>
                <Input
                  id="canvas-url"
                  type="url"
                  placeholder="https://yourschool.instructure.com"
                  value={canvasUrl}
                  onChange={(e) => setCanvasUrl(e.target.value)}
                  className="rounded-lg"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="access-token">Access Token</Label>
                <Input
                  id="access-token"
                  type="password"
                  placeholder="Your Canvas API token"
                  value={accessToken}
                  onChange={(e) => setAccessToken(e.target.value)}
                  className="rounded-lg"
                />
                <p className="text-xs text-muted-foreground">
                  Generate a token in Canvas: Account → Settings → New Access Token
                </p>
              </div>
            </div>

            <Button
              onClick={() => {
                if (canvasUrl && accessToken) {
                  setStep(2);
                } else {
                  toast.error("Please fill in all fields");
                }
              }}
              className="w-full rounded-xl"
            >
              Continue
            </Button>
          </div>
        </Card>
      )}

      {/* Step 2: Syncing */}
      {step === 2 && (
        <Card className="border-border bg-card p-6 shadow-card">
          <div className="space-y-6">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-accent/10">
                <BookOpen className="h-5 w-5 text-accent" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground">Sync Courses</h3>
                <p className="text-sm text-muted-foreground">Importing your courses and assignments</p>
              </div>
            </div>

            <div className="flex flex-col items-center justify-center py-8">
              {!isConnecting ? (
                <Button
                  onClick={handleConnect}
                  className="gap-2 rounded-xl bg-gradient-to-r from-primary to-accent shadow-md"
                >
                  <Link2 className="h-4 w-4" />
                  Start Sync
                </Button>
              ) : (
                <div className="space-y-4 text-center">
                  <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent" />
                  <p className="text-sm text-muted-foreground">Connecting to Canvas...</p>
                </div>
              )}
            </div>
          </div>
        </Card>
      )}

      {/* Step 3: Success */}
      {step === 3 && (
        <div className="animate-slide-up space-y-4">
          <Card className="border-success/30 bg-success/5 p-6 shadow-card">
            <div className="flex items-center gap-3">
              <CheckCircle2 className="h-8 w-8 text-success" />
              <div>
                <h3 className="font-semibold text-foreground">Successfully Connected!</h3>
                <p className="text-sm text-muted-foreground">
                  {syncedCourses.length} courses synced
                </p>
              </div>
            </div>
          </Card>

          <div className="space-y-3">
            <h3 className="font-semibold text-foreground">Synced Courses</h3>
            {syncedCourses.map((course, index) => (
              <Card
                key={course.id}
                className="animate-slide-up border-border bg-card p-4 shadow-card"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <BookOpen className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <h4 className="font-medium text-foreground">{course.name}</h4>
                      <p className="text-sm text-muted-foreground">
                        {course.assignments} upcoming assignments
                      </p>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          <Button
            onClick={() => window.location.href = "/"}
            className="w-full rounded-xl"
          >
            Go to Dashboard
          </Button>
        </div>
      )}
    </div>
  );
};

export default ConnectCanvas;
