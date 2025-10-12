"use client"

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Clock } from "lucide-react";
import { useState, useEffect } from "react";
import { useSession } from "next-auth/react";
import { format, isToday, isTomorrow, parseISO } from "date-fns";

interface CalendarEvent {
  id: string;
  title: string;
  start_time: string;
  end_time: string;
  event_type: string;
  priority: string;
  location?: string;
}

const UpcomingEventsList = () => {
  const { data: session } = useSession();
  const [filter, setFilter] = useState<"all" | "academic">("all");
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEvents = async () => {
      if (!session) return;

      try {
        // Fetch upcoming events for next 7 days, limit to 10
        const response = await fetch('/api/backend/calendar/events/upcoming?days=7&limit=10');
        if (response.ok) {
          const data = await response.json();
          setEvents(data);
        }
      } catch (error) {
        console.error('Failed to fetch upcoming events:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, [session]);

  const filteredEvents = filter === "all" ? events : events.filter(e => e.event_type === "academic");

  const getTypeVariant = (type: string) => {
    switch (type) {
      case "academic": return "destructive";
      case "study_block": return "default";
      case "personal": return "secondary";
      case "social": return "outline";
      case "wellness": return "outline";
      default: return "default";
    }
  };

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      academic: "Academic",
      study_block: "Study",
      break: "Break",
      personal: "Personal",
      social: "Social",
      wellness: "Wellness",
      other: "Other"
    };
    return labels[type] || type;
  };

  const formatEventTime = (startTime: string) => {
    const date = parseISO(startTime);
    if (isToday(date)) {
      return `Today, ${format(date, 'h:mm a')}`;
    } else if (isTomorrow(date)) {
      return `Tomorrow, ${format(date, 'h:mm a')}`;
    } else {
      return format(date, 'MMM d, h:mm a');
    }
  };

  if (loading) {
    return (
      <Card className="border-2 border-border p-4 shadow-card bg-card">
        <h3 className="text-sm font-semibold text-foreground mb-4">Upcoming Events</h3>
        <p className="text-xs text-muted-foreground">Loading events...</p>
      </Card>
    );
  }

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
            variant={filter === "academic" ? "default" : "ghost"}
            size="sm"
            className="h-7 text-xs"
            onClick={() => setFilter("academic")}
          >
            Academic
          </Button>
        </div>
      </div>

      <div className="space-y-3">
        {filteredEvents.length === 0 ? (
          <p className="text-xs text-muted-foreground text-center py-4">
            No upcoming events
          </p>
        ) : (
          filteredEvents.map((event) => (
            <div
              key={event.id}
              className="p-3 rounded-lg border-2 border-border bg-card hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-foreground truncate">{event.title}</p>
                  <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                    <Clock className="h-3 w-3" />
                    {formatEventTime(event.start_time)}
                  </p>
                  {event.location && (
                    <p className="text-xs text-muted-foreground mt-1">{event.location}</p>
                  )}
                </div>
                <Badge variant={getTypeVariant(event.event_type)} className="text-xs flex-shrink-0">
                  {getTypeLabel(event.event_type)}
                </Badge>
              </div>
            </div>
          ))
        )}
      </div>
    </Card>
  );
};

export default UpcomingEventsList;
