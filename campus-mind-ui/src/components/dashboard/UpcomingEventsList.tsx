"use client"

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Clock } from "lucide-react";
import { useState } from "react";

interface Event {
  id: number;
  title: string;
  time: string;
  type: "exam" | "class" | "study" | "personal";
}

const UpcomingEventsList = () => {
  const [filter, setFilter] = useState<"all" | "exams">("all");
  
  const events: Event[] = [
    { id: 1, title: "Linear Algebra Exam", time: "Oct 17, 2:00 PM", type: "exam" },
    { id: 2, title: "CS228 Lecture", time: "Today, 10:00 AM", type: "class" },
    { id: 3, title: "Study Group - Physics", time: "Today, 4:00 PM", type: "study" },
    { id: 4, title: "Club Meeting", time: "Tomorrow, 3:00 PM", type: "personal" },
  ];

  const filteredEvents = filter === "all" ? events : events.filter(e => e.type === "exam");

  const getTypeVariant = (type: string) => {
    switch (type) {
      case "exam": return "destructive";
      case "class": return "secondary";
      case "study": return "default";
      case "personal": return "outline";
      default: return "default";
    }
  };

  const getTypeLabel = (type: string) => {
    return type.charAt(0).toUpperCase() + type.slice(1);
  };

  return (
    <Card className="border-2 border-border p-4 shadow-card bg-card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-foreground">Upcoming Events</h3>
        <div className="flex gap-2">
          <Button
            variant={filter === "all" ? "default" : "ghost"}
            size="sm"
            className="h-7 text-xs"
            onClick={() => setFilter("all")}
          >
            All
          </Button>
          <Button
            variant={filter === "exams" ? "default" : "ghost"}
            size="sm"
            className="h-7 text-xs"
            onClick={() => setFilter("exams")}
          >
            Exams
          </Button>
        </div>
      </div>

      <div className="space-y-3">
        {filteredEvents.map((event) => (
          <div
            key={event.id}
            className="p-3 rounded-lg border-2 border-border bg-card hover:bg-muted/50 transition-colors"
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-foreground truncate">{event.title}</p>
                <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                  <Clock className="h-3 w-3" />
                  {event.time}
                </p>
              </div>
              <Badge variant={getTypeVariant(event.type)} className="text-xs flex-shrink-0">
                {getTypeLabel(event.type)}
              </Badge>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};

export default UpcomingEventsList;
