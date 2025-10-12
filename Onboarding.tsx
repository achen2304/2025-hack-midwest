import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Calendar, ExternalLink, CheckCircle2, ArrowRight, Brain } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export default function Onboarding() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [canvasUrl, setCanvasUrl] = useState("");
  const [canvasToken, setCanvasToken] = useState("");
  const [canvasConnected, setCanvasConnected] = useState(false);
  const [googleConnected, setGoogleConnected] = useState(false);

  const handleCanvasConnect = () => {
    if (!canvasUrl || !canvasToken) {
      toast({
        title: "Missing information",
        description: "Please enter both Canvas URL and access token.",
        variant: "destructive",
      });
      return;
    }

    // Simulate connection
    setCanvasConnected(true);
    toast({
      title: "Canvas connected! ✅",
      description: "Your courses will be synced automatically.",
    });
  };

  const handleGoogleConnect = () => {
    // Simulate Google Calendar OAuth
    setGoogleConnected(true);
    toast({
      title: "Google Calendar connected! ✅",
      description: "Your events will appear in your schedule.",
    });
  };

  const handleContinue = () => {
    navigate("/dashboard");
  };

  const handleSkip = () => {
    navigate("/dashboard");
  };

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
          <p className="text-muted-foreground">Let's connect your accounts to get started</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-6">
          {/* Canvas Connection */}
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
              <CardDescription>
                Sync your courses, assignments, and deadlines
              </CardDescription>
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
                      <li>Scroll to "Approved Integrations"</li>
                      <li>Click "+ New Access Token"</li>
                      <li>Copy and paste the token here</li>
                    </ol>
                  </div>
                  <Button onClick={handleCanvasConnect} className="w-full">
                    Connect Canvas
                  </Button>
                </>
              ) : (
                <div className="text-center py-6">
                  <CheckCircle2 className="h-12 w-12 text-primary mx-auto mb-2" />
                  <p className="font-medium">Canvas Connected</p>
                  <p className="text-sm text-muted-foreground">Your courses are syncing</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Google Calendar Connection */}
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
              <CardDescription>
                Import your schedule and events automatically
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {!googleConnected ? (
                <>
                  <div className="bg-muted/50 rounded-lg p-3 text-xs space-y-1">
                    <p className="font-medium">What you'll get:</p>
                    <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                      <li>Auto-sync class schedules</li>
                      <li>View all events in one place</li>
                      <li>Smart scheduling recommendations</li>
                      <li>Never miss an important date</li>
                    </ul>
                  </div>
                  <div className="bg-muted/50 rounded-lg p-3 text-xs space-y-1">
                    <p className="font-medium">How it works:</p>
                    <ol className="list-decimal list-inside space-y-1 text-muted-foreground">
                      <li>Click "Connect Google Calendar"</li>
                      <li>Sign in with your Google account</li>
                      <li>Grant calendar access permission</li>
                      <li>Your events sync automatically</li>
                    </ol>
                  </div>
                  <Button onClick={handleGoogleConnect} variant="outline" className="w-full">
                    <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
                      <path
                        fill="currentColor"
                        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                      />
                      <path
                        fill="currentColor"
                        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                      />
                      <path
                        fill="currentColor"
                        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                      />
                      <path
                        fill="currentColor"
                        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                      />
                    </svg>
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
            onClick={handleContinue} 
            size="lg"
            disabled={!canvasConnected && !googleConnected}
          >
            Continue to Dashboard
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
