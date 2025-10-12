"use client"

import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useState } from "react";
import { CheckCircle2 } from "lucide-react";

interface Task {
  id: number;
  title: string;
  course: string;
  dueDate: string;
  priority: "high" | "medium" | "low";
  completed: boolean;
}

const TaskList = () => {
  const [tasks, setTasks] = useState<Task[]>([
    {
      id: 1,
      title: "Complete Binary Trees Assignment",
      course: "CS 101",
      dueDate: "Today, 11:59 PM",
      priority: "high",
      completed: false,
    },
    {
      id: 2,
      title: "Read Chapter 7: Integration",
      course: "MATH 201",
      dueDate: "Tomorrow",
      priority: "medium",
      completed: false,
    },
    {
      id: 3,
      title: "Psychology Quiz Prep",
      course: "PSY 101",
      dueDate: "Today, 5:00 PM",
      priority: "high",
      completed: false,
    },
    {
      id: 4,
      title: "Lab Report Draft",
      course: "CHEM 151",
      dueDate: "Friday",
      priority: "low",
      completed: false,
    },
  ]);

  const toggleTask = (id: number) => {
    setTasks(
      tasks.map((task) =>
        task.id === id ? { ...task, completed: !task.completed } : task
      )
    );
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "destructive";
      case "medium":
        return "default";
      case "low":
        return "secondary";
      default:
        return "default";
    }
  };

  const todayTasks = tasks.filter((t) => t.dueDate.includes("Today"));
  const weekTasks = tasks.filter((t) => !t.completed);

  return (
    <Card className="border-2 border-border p-6 shadow-card bg-card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <CheckCircle2 className="h-5 w-5 text-primary" />
          <h3 className="text-lg font-semibold text-foreground">Tasks & Assignments</h3>
        </div>
      </div>

      <Tabs defaultValue="today" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="today">Due Today</TabsTrigger>
          <TabsTrigger value="week">This Week</TabsTrigger>
          <TabsTrigger value="all">All Tasks</TabsTrigger>
        </TabsList>

        <TabsContent value="today" className="space-y-3 mt-4">
          {todayTasks.map((task) => (
            <div
              key={task.id}
              className="flex items-start gap-3 p-3 rounded-lg hover:bg-muted/50 transition-colors border-2 border-border"
            >
              <Checkbox
                checked={task.completed}
                onCheckedChange={() => toggleTask(task.id)}
                className="mt-1"
              />
              <div className="flex-1">
                <p
                  className={`text-sm font-medium ${
                    task.completed ? "line-through text-muted-foreground" : "text-foreground"
                  }`}
                >
                  {task.title}
                </p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs text-muted-foreground">{task.course}</span>
                  <span className="text-xs text-muted-foreground">•</span>
                  <span className="text-xs text-muted-foreground">{task.dueDate}</span>
                </div>
              </div>
              <Badge variant={getPriorityColor(task.priority)} className="text-xs">
                {task.priority}
              </Badge>
            </div>
          ))}
        </TabsContent>

        <TabsContent value="week" className="space-y-3 mt-4">
          {weekTasks.map((task) => (
            <div
              key={task.id}
              className="flex items-start gap-3 p-3 rounded-lg hover:bg-muted/50 transition-colors border-2 border-border"
            >
              <Checkbox
                checked={task.completed}
                onCheckedChange={() => toggleTask(task.id)}
                className="mt-1"
              />
              <div className="flex-1">
                <p className="text-sm font-medium text-foreground">{task.title}</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs text-muted-foreground">{task.course}</span>
                  <span className="text-xs text-muted-foreground">•</span>
                  <span className="text-xs text-muted-foreground">{task.dueDate}</span>
                </div>
              </div>
              <Badge variant={getPriorityColor(task.priority)} className="text-xs">
                {task.priority}
              </Badge>
            </div>
          ))}
        </TabsContent>

        <TabsContent value="all" className="space-y-3 mt-4">
          {tasks.map((task) => (
            <div
              key={task.id}
              className="flex items-start gap-3 p-3 rounded-lg hover:bg-muted/50 transition-colors border-2 border-border"
            >
              <Checkbox
                checked={task.completed}
                onCheckedChange={() => toggleTask(task.id)}
                className="mt-1"
              />
              <div className="flex-1">
                <p
                  className={`text-sm font-medium ${
                    task.completed ? "line-through text-muted-foreground" : "text-foreground"
                  }`}
                >
                  {task.title}
                </p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs text-muted-foreground">{task.course}</span>
                  <span className="text-xs text-muted-foreground">•</span>
                  <span className="text-xs text-muted-foreground">{task.dueDate}</span>
                </div>
              </div>
              <Badge variant={getPriorityColor(task.priority)} className="text-xs">
                {task.priority}
              </Badge>
            </div>
          ))}
        </TabsContent>
      </Tabs>
    </Card>
  );
};

export default TaskList;
