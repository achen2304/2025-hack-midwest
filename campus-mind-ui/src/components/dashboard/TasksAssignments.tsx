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
  time: string;
  priority: "high" | "medium" | "low";
  completed: boolean;
  dueToday?: boolean;
}

const TasksAssignments = () => {
  const [tasks, setTasks] = useState<Task[]>([
    {
      id: 1,
      title: "Complete Binary Trees Assignment",
      course: "CS 101",
      time: "Today, 11:59 PM",
      priority: "high",
      completed: false,
      dueToday: true,
    },
    {
      id: 2,
      title: "Psychology Quiz Prep",
      course: "PSY 101",
      time: "Today, 5:00 PM",
      priority: "high",
      completed: false,
      dueToday: true,
    },
    {
      id: 3,
      title: "Read Chapter 7: Integration",
      course: "MATH 201",
      time: "Tomorrow",
      priority: "medium",
      completed: false,
    },
    {
      id: 4,
      title: "Lab Report Draft",
      course: "CHEM 151",
      time: "Friday",
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

  const getPriorityVariant = (priority: string) => {
    switch (priority) {
      case "high": return "destructive";
      case "medium": return "default";
      case "low": return "secondary";
      default: return "default";
    }
  };

  const todayTasks = tasks.filter((t) => t.dueToday);
  const weekTasks = tasks.filter((t) => !t.completed);

  const renderTask = (task: Task) => (
    <div
      key={task.id}
      className="flex items-start gap-3 p-4 rounded-lg border-2 border-border bg-card hover:bg-muted/50 transition-colors"
    >
      <Checkbox
        checked={task.completed}
        onCheckedChange={() => toggleTask(task.id)}
        className="mt-1"
      />
      <div className="flex-1 min-w-0">
        <p className={`text-sm font-medium ${task.completed ? "line-through text-muted-foreground" : "text-foreground"}`}>
          {task.title}
        </p>
        <p className="text-xs text-muted-foreground mt-1">
          {task.course} • {task.time}
        </p>
      </div>
      <Badge variant={getPriorityVariant(task.priority)} className="text-xs flex-shrink-0">
        {task.priority}
      </Badge>
    </div>
  );

  return (
    <Card className="border-2 border-border p-6 shadow-card bg-card">
      <div className="flex items-center gap-2 mb-4">
        <CheckCircle2 className="h-5 w-5 text-primary" />
        <h3 className="text-lg font-semibold text-foreground">Tasks & Assignments</h3>
      </div>

      <Tabs defaultValue="today" className="w-full">
        <TabsList className="grid w-full grid-cols-3 mb-4">
          <TabsTrigger value="today">Due Today</TabsTrigger>
          <TabsTrigger value="week">This Week</TabsTrigger>
          <TabsTrigger value="all">All Tasks</TabsTrigger>
        </TabsList>

        <TabsContent value="today" className="space-y-3 mt-0">
          {todayTasks.map(renderTask)}
        </TabsContent>

        <TabsContent value="week" className="space-y-3 mt-0">
          {weekTasks.map(renderTask)}
        </TabsContent>

        <TabsContent value="all" className="space-y-3 mt-0">
          {tasks.map(renderTask)}
        </TabsContent>
      </Tabs>
    </Card>
  );
};

export default TasksAssignments;
