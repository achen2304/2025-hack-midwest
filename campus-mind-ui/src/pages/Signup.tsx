"use client"

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { AuthCard } from "@/components/auth/AuthCard";
import { PasswordInput } from "@/components/auth/PasswordInput";
import { ErrorBanner } from "@/components/auth/ErrorBanner";
import { SocialAuthButtons } from "@/components/auth/SocialAuthButtons";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage, FormDescription } from "@/components/ui/form";
import { Loader2, Brain } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { signIn, useSession } from "next-auth/react";

const signupSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Please enter a valid email address"),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .regex(/[A-Z]/, "Password must contain at least one uppercase letter")
    .regex(/[0-9]/, "Password must contain at least one number")
    .regex(/[^A-Za-z0-9]/, "Password must contain at least one special character"),
  confirmPassword: z.string(),
  agreedToTerms: z.boolean().refine((val) => val === true, {
    message: "You must agree to the Terms and Privacy Policy",
  }),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type SignupForm = z.infer<typeof signupSchema>;

export default function Signup() {
  const router = useRouter();
  const { toast } = useToast();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const sessionState = useSession();
  const status = sessionState?.status;
  const session = sessionState?.data;

  const form = useForm<SignupForm>({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      name: "",
      email: "",
      password: "",
      confirmPassword: "",
      agreedToTerms: false,
    },
  });


  const [err, setErr] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  const handleSocialAuth = (provider: string) => {
    signIn('google', {callbackUrl: '/dashboard' });
  };

  async function onSubmit(e: React.FormEvent) {
    setErr(null);

    startTransition(async () => {
      const res = await fetch('/api/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: form.getValues("name"), email: form.getValues("email"), password: form.getValues("password") }),
      });
      const data = await res.json();

      if (!res.ok) {
        setErr(data?.error || 'Failed to sign up');
        return;
      }

      toast({
        title: "Account created! 🎉",
        description: "Welcome to CampusMind. Let's get started!",
      });
      

      // Sign in after signup
      const login = await signIn('credentials', { email: form.getValues("email"), password: form.getValues("password"), redirect: true, callbackUrl: "/onboarding" });
      if (login?.error) {
        // If auto-login fails, return
        return;
      }
      return;
    });
  }

  if (status === "loading") {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <Loader2 className="h-12 w-12 text-primary animate-spin" />
        </div>
      );
    }

  if (session) {
    router.push('/dashboard');
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      <header className="fixed top-0 left-0 right-0 z-50 glass-card border-b">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="relative">
              <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full" />
              <Brain className="h-8 w-8 text-primary relative animate-float" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              CampusMind
            </span>
          </Link>
          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="ghost" size="sm">Log In</Button>
            </Link>
            <Link href="/signup">
              <Button size="sm">Sign Up</Button>
            </Link>
          </div>
        </div>
      </header>

      <AuthCard
        title="Create your account"
        description="Start planning smarter today"
        footer={
          <div className="space-y-4">
            <p className="text-center text-sm text-muted-foreground">
              Already have an account?{" "}
              <Link href="/login" className="text-primary hover:underline font-medium">
                Log in
              </Link>
            </p>
          </div>
        }
      >
        {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Name</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Your full name"
                      autoComplete="name"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input
                      type="email"
                      placeholder="you@university.edu"
                      autoComplete="email"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Password</FormLabel>
                  <FormControl>
                    <PasswordInput
                      placeholder="Create a strong password"
                      autoComplete="new-password"
                      showStrength
                      {...field}
                    />
                  </FormControl>
                  <FormDescription className="text-xs">
                    Must include: 8+ characters, uppercase, number, and special character
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="confirmPassword"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Confirm Password</FormLabel>
                  <FormControl>
                    <PasswordInput
                      placeholder="Re-enter your password"
                      autoComplete="new-password"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="agreedToTerms"
              render={({ field }) => (
                <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                  <FormControl>
                    <Checkbox
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                  <div className="space-y-1 leading-none">
                    <FormLabel className="text-sm font-normal">
                      I agree to the{" "}
                      <a href="/terms" className="text-primary hover:underline">
                        Terms
                      </a>{" "}
                      and{" "}
                      <a href="/privacy" className="text-primary hover:underline">
                        Privacy Policy
                      </a>
                    </FormLabel>
                    <FormMessage />
                  </div>
                </FormItem>
              )}
            />

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating account...
                </>
              ) : (
                "Create account"
              )}
            </Button>
          </form>
        </Form>

        <SocialAuthButtons
          onGoogleClick={() => handleSocialAuth("google")}
          onMicrosoftClick={() => handleSocialAuth("microsoft")}
          isLoading={isLoading}
        />
      </AuthCard>

      <footer className="fixed bottom-0 left-0 right-0 bg-muted/30 border-t py-4">
        <div className="container mx-auto px-4 flex justify-center gap-6 text-sm text-muted-foreground">
          <a href="/privacy" className="hover:text-foreground transition-colors">Privacy</a>
          <a href="/terms" className="hover:text-foreground transition-colors">Terms</a>
          <a href="/contact" className="hover:text-foreground transition-colors">Contact</a>
          <span>© CampusMind 2025</span>
        </div>
      </footer>
    </div>
  );
}
