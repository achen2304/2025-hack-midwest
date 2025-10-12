"use client"

import { LayoutGrid, BookOpen, Heart, Calendar, Settings, Brain, Flame, Sparkles } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
  SidebarFooter,
} from "@/components/ui/sidebar";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

const items = [
  { title: "Dashboard", url: "/dashboard", icon: LayoutGrid },
  { title: "Study Planner", url: "/dashboard/study", icon: BookOpen },
  { title: "Wellness", url: "/dashboard/wellness", icon: Heart },
  { title: "Calendar", url: "/dashboard/connect", icon: Calendar },
  { title: "Settings", url: "/dashboard/settings", icon: Settings },
];

export function AppSidebar() {
  const { state } = useSidebar();
  const pathname = usePathname();
  const isCollapsed = state === "collapsed";

  return (
    <Sidebar className="border-r-2 border-border bg-muted/30">
      <div className="p-4 border-b-2 border-border">
        <div className="flex items-center gap-2.5">
          <div className="relative">
            <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full" />
            <Brain className="h-8 w-8 text-primary relative" />
          </div>
          {!isCollapsed && (
            <span className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              CampusMind
            </span>
          )}
        </div>
      </div>

      <SidebarContent className="p-4">
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => {
                const isActive = pathname === item.url || (item.url === "/dashboard" && pathname === "/dashboard");
                return (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton asChild>
                      <Link
                        href={item.url}
                        className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                          isActive
                            ? "bg-primary text-primary-foreground font-medium shadow-glow"
                            : "text-muted-foreground hover:text-foreground hover:bg-primary/5"
                        }`}
                      >
                        <item.icon className="h-5 w-5 flex-shrink-0" />
                        {!isCollapsed && <span className="flex-1">{item.title}</span>}
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {!isCollapsed && (
          <div className="mt-8 space-y-4">
            {/* Streak Counter */}
            <Card className="border-2 border-border p-4 bg-gradient-to-br from-orange-500/10 to-red-500/10 h-[100px]">
              <div className="flex items-center gap-3">
                <Flame className="h-6 w-6 text-orange-500 animate-pulse" />
                <div>
                  <div className="text-2xl font-bold text-foreground">10</div>
                  <div className="text-xs text-muted-foreground">Day Streak</div>
                </div>
              </div>
            </Card>

            {/* XP Bar */}
            <Card className="border-2 border-border p-4 bg-card h-[100px]">
              <div className="flex items-center gap-2 mb-3">
                <Sparkles className="h-5 w-5 text-accent" />
                <span className="text-base font-bold text-foreground">Level 5</span>
              </div>
              <Progress value={75} className="h-2 mb-2" />
              <div className="text-xs text-muted-foreground text-right">450 / 600 XP</div>
            </Card>

            {/* AI Agents Status */}
            <Card className="border-2 border-border p-4 shadow-card bg-card h-[100px]">
              <div className="flex items-center gap-2 mb-3">
                <Brain className="h-5 w-5 text-primary" />
                <span className="text-base font-bold text-foreground">AI Agents</span>
                <div className="ml-auto w-2.5 h-2.5 rounded-full bg-success animate-pulse" />
              </div>

              <div className="grid grid-cols-4 gap-1.5">
                {[
                  { icon: "📆", name: "Schedule" },
                  { icon: "📘", name: "Study" },
                  { icon: "❤️", name: "Wellness" },
                  { icon: "🧠", name: "Context" },
                ].map((agent) => (
                  <div
                    key={agent.name}
                    className="flex items-center justify-center"
                    title={`${agent.name} Agent`}
                  >
                    <div className="w-9 h-9 rounded-full border-2 border-success/30 bg-success/5 flex items-center justify-center hover:scale-110 transition-all">
                      <span className="text-lg">{agent.icon}</span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}
      </SidebarContent>

      {!isCollapsed && (
        <SidebarFooter className="p-4 border-t-2 border-border">
          <div className="text-xs text-center text-muted-foreground">
            <p>CampusMind Beta v0.3</p>
            <p className="mt-1">Hackathon Build</p>
          </div>
        </SidebarFooter>
      )}
    </Sidebar>
  );
}
