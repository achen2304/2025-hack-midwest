import { Card } from "@/components/ui/card";
import { Calendar, Clock, MapPin } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";

interface Event {
  id: number;
  title: string;
  time: string;
  location?: string;
  color: string;
}

const UpcomingEvents = () => {
  const events: Event[] = [
    {
      id: 1,
      title: "CS 101 Lecture",
      time: "10:00 AM - 11:30 AM",
      location: "Room 204",
      color: "bg-primary/10 border-primary/30",
    },
    {
      id: 2,
      title: "Study Group",
      time: "2:00 PM - 3:30 PM",
      location: "Library",
      color: "bg-accent/10 border-accent/30",
    },
    {
      id: 3,
      title: "Wellness Session",
      time: "5:00 PM - 5:30 PM",
      location: "Online",
      color: "bg-success/10 border-success/30",
    },
    {
      id: 4,
      title: "Math Tutorial",
      time: "7:00 PM - 8:00 PM",
      location: "Room 105",
      color: "bg-warning/10 border-warning/30",
    },
  ];

  return (
    <Card className="border-2 border-border p-6 shadow-card bg-card">
      <div className="flex items-center gap-2 mb-4">
        <Calendar className="h-5 w-5 text-primary" />
        <h3 className="text-base font-semibold text-foreground">Upcoming Events</h3>
      </div>

      <ScrollArea className="h-[280px] pr-4">
        <div className="space-y-3">
          {events.map((event) => (
            <div
              key={event.id}
              className={`p-4 rounded-xl border-2 ${event.color} transition-all hover:scale-105`}
            >
              <h4 className="font-semibold text-foreground text-sm mb-2">{event.title}</h4>
              <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                <Clock className="h-3 w-3" />
                <span>{event.time}</span>
              </div>
              {event.location && (
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <MapPin className="h-3 w-3" />
                  <span>{event.location}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      </ScrollArea>

      <div className="mt-4 pt-4 border-t-2 border-border">
        <button className="w-full text-sm font-medium text-primary hover:text-primary/80 transition-colors">
          View Full Calendar →
        </button>
      </div>
    </Card>
  );
};

export default UpcomingEvents;
