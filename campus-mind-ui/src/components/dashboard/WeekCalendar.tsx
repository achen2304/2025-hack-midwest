import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Check, Plus } from "lucide-react";

const WeekCalendar = () => {
  const days = [
    { day: "Sun", date: 5 },
    { day: "Mon", date: 6 },
    { day: "Tue", date: 7 },
    { day: "Wed", date: 8 },
    { day: "Thu", date: 9 },
    { day: "Fri", date: 10 },
    { day: "Sat", date: 11, isToday: true },
  ];

  return (
    <Card className="border-2 border-border p-4 shadow-card bg-card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-foreground">This Week</h3>
        <Button variant="ghost" size="sm" className="h-7 text-xs">
          <Check className="h-3 w-3 mr-1" />
          Synced
        </Button>
      </div>

      <div className="grid grid-cols-7 gap-2 mb-4">
        {days.map((day) => (
          <div key={day.date} className="flex flex-col items-center">
            <span className="text-xs text-muted-foreground mb-1">{day.day}</span>
            <button
              className={`w-8 h-8 rounded-full text-sm font-semibold transition-colors ${
                day.isToday
                  ? "bg-primary text-primary-foreground"
                  : "hover:bg-muted text-foreground"
              }`}
            >
              {day.date}
            </button>
          </div>
        ))}
      </div>

      <Button variant="outline" className="w-full border-2" size="sm">
        <Plus className="h-3 w-3 mr-2" />
        Add study block
      </Button>
    </Card>
  );
};

export default WeekCalendar;
