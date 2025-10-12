import Link from "next/link";
import { Brain, BookOpen, Heart, Calendar, Flame, Target, Sparkles, ArrowRight, CheckCircle2, MessageSquare, Zap, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";

const Landing = () => {
  const features = [
    {
      icon: BookOpen,
      title: "AI Study Planner",
      description: "Personalized schedules automatically generated from your Canvas and Google Calendar data.",
    },
    {
      icon: Heart,
      title: "Wellness Tracker",
      description: "Balance mental health with workload through integrated mood tracking and insights.",
    },
    {
      icon: Brain,
      title: "Agentic AI",
      description: "Intelligent tutor and planner that learns your habits and adapts to your learning style.",
    },
    {
      icon: Calendar,
      title: "Smart Calendar Integration",
      description: "Auto-sync with Google Calendar and Canvas for seamless schedule management.",
    },
    {
      icon: Flame,
      title: "Gamified Progress",
      description: "Stay motivated with streaks, XP points, and badges as you achieve your goals.",
    },
  ];

  const howItWorksSteps = [
    {
      number: 1,
      title: "Create Account & Connect",
      description: "Sign up and connect your school tools (Google Calendar and Canvas).",
    },
    {
      number: 2,
      title: "Set Your Goals",
      description: "Add your classes, deadlines, and personal academic goals.",
    },
    {
      number: 3,
      title: "Get Your Plan",
      description: "Let CampusMind build your personalized weekly study schedule.",
    },
    {
      number: 4,
      title: "Track & Learn",
      description: "Monitor progress and chat with your AI tutor for guidance.",
    },
  ];

  const integrations = [
    { name: "Google Calendar", logo: "🗓️" },
    { name: "Canvas LMS", logo: "📚" },
    { name: "Notion", logo: "📝" },
    { name: "AWS Strands AI", logo: "🤖" },
  ];

  const testimonials = [
    {
      name: "Sarah Chen",
      major: "Computer Science, Junior",
      quote: "CampusMind helped me balance 18 credits and stay organized without burning out.",
    },
    {
      name: "Marcus Johnson",
      major: "Biology, Sophomore",
      quote: "The AI tutor feature is incredible. It's like having a study buddy available 24/7.",
    },
    {
      name: "Elena Rodriguez",
      major: "Business Administration, Senior",
      quote: "I finally stopped missing deadlines. The Canvas integration is a game-changer.",
    },
  ];

  const faqs = [
    {
      question: "How does CampusMind sync with Canvas?",
      answer: "CampusMind securely connects to your Canvas account using OAuth authentication. Once connected, it automatically pulls your course schedules, assignments, and deadlines to build your personalized study plan.",
    },
    {
      question: "Is my data private?",
      answer: "Absolutely. We use enterprise-grade encryption and never share your personal data with third parties. Your calendar events and study information are stored securely and only used to enhance your experience.",
    },
    {
      question: "Can I use it on multiple devices?",
      answer: "Yes! CampusMind works seamlessly across desktop, tablet, and mobile devices. Your data syncs automatically so you can access your study plans anywhere.",
    },
    {
      question: "Is there a free plan for students?",
      answer: "Yes! We offer a free tier for all students with core features including study planning, calendar sync, and basic AI assistance. Premium features are available for advanced analytics and unlimited AI tutoring.",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      {/* Animated Background */}
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-primary/10 via-transparent to-accent/5 pointer-events-none" />
      
      {/* Header */}
      <header className="sticky top-0 z-50 bg-background/80 backdrop-blur-sm border-b border-border/50">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center gap-8">
              <div className="flex items-center gap-2.5">
                <div className="relative">
                  <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full" />
                  <Brain className="h-8 w-8 text-primary relative animate-float" />
                </div>
                <span className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                  CampusMind
                </span>
              </div>
              
              <nav className="hidden md:flex items-center gap-6">
                <a href="#features" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
                  Features
                </a>
                <a href="#how-it-works" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
                  How It Works
                </a>
                <a href="#faq" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
                  FAQ
                </a>
                <a href="#footer" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
                  Contact
                </a>
              </nav>
            </div>
            
            <div className="flex items-center gap-3">
              <Link href="/login">
                <Button variant="ghost" size="sm">
                  Log In
                </Button>
              </Link>
              <Link href="/signup">
                <Button size="sm" className="gap-2">
                  Sign Up
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main className="relative">
        {/* Hero Section */}
        <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pt-20 pb-24">
          <div className="grid gap-12 lg:grid-cols-2 lg:gap-16 items-center">
            <div className="animate-fade-in space-y-8">
              <div className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-2 text-sm font-medium text-primary border border-primary/20">
                <Sparkles className="h-4 w-4" />
                AI-Powered Student Assistant
              </div>
              
              <h1 className="text-5xl font-bold leading-tight text-foreground lg:text-6xl">
                Your AI-powered student productivity and wellness companion
              </h1>
              
              <p className="text-lg text-muted-foreground max-w-xl">
                CampusMind helps college students balance academic workload with mental wellness through 
                intelligent scheduling, AI tutoring, and seamless integration with Google Calendar and Canvas.
              </p>
              
              <p className="text-sm text-muted-foreground max-w-xl">
                Available for college students using Google Calendar and Canvas
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4">
                <Link href="/signup">
                  <Button size="lg" className="gap-2 text-base w-full sm:w-auto">
                    Get Started
                    <ArrowRight className="h-5 w-5" />
                  </Button>
                </Link>
                <a href="#how-it-works">
                  <Button variant="outline" size="lg" className="text-base w-full sm:w-auto">
                    Learn More
                  </Button>
                </a>
              </div>

              <div className="flex items-center gap-6 pt-4">
                <div className="flex -space-x-2">
                  {[1, 2, 3, 4].map((i) => (
                    <div
                      key={i}
                      className="h-10 w-10 rounded-full bg-gradient-to-br from-primary to-accent border-2 border-background"
                    />
                  ))}
                </div>
                <div className="text-sm">
                  <div className="font-semibold text-foreground">2,000+ students</div>
                  <div className="text-muted-foreground">leveling up their academics</div>
                </div>
              </div>
            </div>

            <div className="relative animate-slide-up" style={{ animationDelay: "150ms" }}>
              <div className="absolute -inset-4 bg-gradient-to-r from-primary/20 to-accent/20 rounded-3xl blur-2xl" />
              <Card className="relative gradient-border bg-card p-8 shadow-card-hover">
                <div className="space-y-6">
                  <div className="flex items-center gap-3">
                    <div className="p-3 rounded-xl bg-primary/10">
                      <Target className="h-6 w-6 text-primary" />
                    </div>
                    <div>
                      <div className="text-sm font-medium text-muted-foreground">Today&apos;s Goal</div>
                      <div className="text-xl font-bold text-foreground">Complete 3 study blocks</div>
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    {[
                      { title: "Data Structures Review", time: "10:00 AM", done: true },
                      { title: "Calculus Problem Set", time: "2:00 PM", done: true },
                      { title: "Chemistry Lab Report", time: "4:30 PM", done: false },
                    ].map((task, i) => (
                      <div
                        key={i}
                        className="flex items-center gap-3 p-3 rounded-lg bg-muted/50 border border-border"
                      >
                        <div
                          className={`h-5 w-5 rounded-full border-2 flex items-center justify-center ${
                            task.done ? "bg-success border-success" : "border-muted-foreground"
                          }`}
                        >
                          {task.done && <div className="h-2 w-2 bg-white rounded-full" />}
                        </div>
                        <div className="flex-1">
                          <div className={`text-sm font-medium ${task.done ? "line-through text-muted-foreground" : "text-foreground"}`}>
                            {task.title}
                          </div>
                          <div className="text-xs text-muted-foreground">{task.time}</div>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="flex items-center justify-between pt-4 border-t border-border">
                    <div className="flex items-center gap-2">
                      <Flame className="h-5 w-5 text-orange-500 animate-pulse" />
                      <span className="text-sm font-semibold text-foreground">10 Day Streak!</span>
                    </div>
                    <div className="text-sm text-muted-foreground">Level 5 • 450/600 XP</div>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </section>

        {/* Key Features Section */}
        <section id="features" className="bg-muted/30 py-20">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12 animate-fade-in">
              <h2 className="text-3xl font-bold text-foreground mb-4">
                Key Features
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Powerful tools designed to help college students succeed academically while maintaining balance.
              </p>
            </div>

            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {features.map((feature, index) => (
                <Card
                  key={index}
                  className="group p-6 shadow-card hover:shadow-card-hover transition-all duration-300 hover:-translate-y-1 animate-slide-up"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <div className="mb-4 inline-flex p-3 rounded-xl bg-gradient-to-br from-primary/10 to-accent/10 group-hover:from-primary/20 group-hover:to-accent/20 transition-colors">
                    <feature.icon className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {feature.description}
                  </p>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* How It Works Section */}
        <section id="how-it-works" className="py-20">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12 animate-fade-in">
              <h2 className="text-3xl font-bold text-foreground mb-4">
                How It Works
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Get started in four simple steps and transform your academic life.
              </p>
            </div>

            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
              {howItWorksSteps.map((step, index) => (
                <div
                  key={index}
                  className="relative animate-slide-up"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <Card className="p-6 h-full shadow-card hover:shadow-card-hover transition-all">
                    <div className="flex flex-col items-center text-center space-y-4">
                      <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white font-bold text-xl">
                        {step.number}
                      </div>
                      <h3 className="text-lg font-semibold text-foreground">
                        {step.title}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {step.description}
                      </p>
                    </div>
                  </Card>
                  {index < howItWorksSteps.length - 1 && (
                    <div className="hidden lg:block absolute top-1/2 -right-4 transform -translate-y-1/2">
                      <ArrowRight className="h-6 w-6 text-primary" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Integrations Section */}
        <section className="bg-muted/30 py-20">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12 animate-fade-in">
              <h2 className="text-3xl font-bold text-foreground mb-4">
                Seamless Integrations
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                CampusMind connects with your favorite tools to automate scheduling, studying, and goal tracking.
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
              {integrations.map((integration, index) => (
                <Card
                  key={index}
                  className="p-8 flex flex-col items-center justify-center text-center space-y-3 shadow-card hover:shadow-card-hover transition-all hover:-translate-y-1 animate-slide-up"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <div className="text-4xl">{integration.logo}</div>
                  <div className="text-sm font-medium text-foreground">
                    {integration.name}
                  </div>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Testimonials Section */}
        <section className="py-20">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12 animate-fade-in">
              <h2 className="text-3xl font-bold text-foreground mb-4">
                What Students Are Saying
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Join thousands of students who are achieving more with less stress.
              </p>
            </div>

            <div className="grid gap-6 md:grid-cols-3">
              {testimonials.map((testimonial, index) => (
                <Card
                  key={index}
                  className="p-6 shadow-card hover:shadow-card-hover transition-all animate-slide-up"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <div className="flex flex-col space-y-4">
                    <div className="flex gap-1">
                      {[1, 2, 3, 4, 5].map((i) => (
                        <Sparkles key={i} className="h-4 w-4 text-accent fill-accent" />
                      ))}
                    </div>
                    <p className="text-sm text-foreground italic">
                      &ldquo;{testimonial.quote}&rdquo;
                    </p>
                    <div className="pt-4 border-t border-border">
                      <div className="font-semibold text-foreground text-sm">
                        {testimonial.name}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {testimonial.major}
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="bg-gradient-to-r from-primary to-accent py-20">
          <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 text-center space-y-8">
            <h2 className="text-4xl font-bold text-primary-foreground">
              Ready to transform your academic life?
            </h2>
            <p className="text-lg text-primary-foreground/90 max-w-2xl mx-auto">
              Join CampusMind today and experience the power of AI-driven productivity and wellness tracking. 
              Start your journey to better grades and less stress.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link href="/signup">
                <Button
                  size="lg"
                  variant="secondary"
                  className="gap-2 text-base bg-white text-primary hover:bg-white/90 shadow-glow w-full sm:w-auto"
                >
                  Sign Up Free
                  <ArrowRight className="h-5 w-5" />
                </Button>
              </Link>
              <Link href="/login">
                <Button
                  size="lg"
                  variant="outline"
                  className="gap-2 text-base border-primary-foreground text-primary-foreground hover:bg-primary-foreground/10 w-full sm:w-auto"
                >
                  Already have an account? Log in
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* FAQ Section */}
        <section id="faq" className="py-20 bg-muted/30">
          <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12 animate-fade-in">
              <h2 className="text-3xl font-bold text-foreground mb-4">
                Frequently Asked Questions
              </h2>
              <p className="text-lg text-muted-foreground">
                Everything you need to know about CampusMind.
              </p>
            </div>

            <Accordion type="single" collapsible className="space-y-4">
              {faqs.map((faq, index) => (
                <AccordionItem
                  key={index}
                  value={`item-${index}`}
                  className="bg-card border border-border rounded-lg px-6 shadow-card"
                >
                  <AccordionTrigger className="text-left hover:no-underline py-4">
                    <span className="font-semibold text-foreground">{faq.question}</span>
                  </AccordionTrigger>
                  <AccordionContent className="text-muted-foreground pb-4">
                    {faq.answer}
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </div>
        </section>

        {/* Footer */}
        <footer id="footer" className="bg-muted/30 py-12 border-t border-border">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <Brain className="h-6 w-6 text-primary" />
                  <span className="font-semibold text-foreground">CampusMind</span>
                </div>
                <p className="text-sm text-muted-foreground">
                  Your AI-powered student productivity and wellness companion.
                </p>
              </div>

              <div>
                <h3 className="font-semibold text-foreground mb-4">Product</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li><a href="#features" className="hover:text-foreground transition-colors">Features</a></li>
                  <li><a href="#how-it-works" className="hover:text-foreground transition-colors">How It Works</a></li>
                  <li><a href="#faq" className="hover:text-foreground transition-colors">FAQ</a></li>
                  <li><Link href="/signup" className="hover:text-foreground transition-colors">Sign Up</Link></li>
                </ul>
              </div>

              <div>
                <h3 className="font-semibold text-foreground mb-4">Company</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li><a href="#" className="hover:text-foreground transition-colors">About</a></li>
                  <li><a href="#footer" className="hover:text-foreground transition-colors">Contact</a></li>
                  <li><a href="#" className="hover:text-foreground transition-colors">Privacy Policy</a></li>
                  <li><a href="#" className="hover:text-foreground transition-colors">Terms of Service</a></li>
                </ul>
              </div>

              <div>
                <h3 className="font-semibold text-foreground mb-4">Contact</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li><a href="mailto:support@campusmind.com" className="hover:text-foreground transition-colors">support@campusmind.com</a></li>
                  <li className="flex gap-3 pt-2">
                    <a href="#" className="hover:text-foreground transition-colors">LinkedIn</a>
                    <a href="#" className="hover:text-foreground transition-colors">GitHub</a>
                    <a href="#" className="hover:text-foreground transition-colors">Twitter</a>
                  </li>
                </ul>
              </div>
            </div>

            <div className="border-t border-border pt-8 text-center text-sm text-muted-foreground">
              © 2025 CampusMind. All rights reserved.
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
};

export default Landing;
