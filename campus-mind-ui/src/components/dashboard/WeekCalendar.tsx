'use client';

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Check, Plus } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import EventCreationModal from './EventCreationModal';
import ClassCreationModal from './ClassCreationModal';

interface CalendarEvent {
  id: string;
  title: string;
  start_time: string;
  end_time: string;
  event_type: string;
  color?: string;
}

const WeekCalendar = () => {
  const { data: session } = useSession();
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentWeek, setCurrentWeek] = useState(new Date());

  // Generate current week dates
  const getWeekDates = (date: Date) => {
    const startOfWeek = new Date(date);
    const day = startOfWeek.getDay();
    const diff = startOfWeek.getDate() - day + (day === 0 ? -6 : 1); // Monday
    startOfWeek.setDate(diff);

    const weekDates = [];
    for (let i = 0; i < 7; i++) {
      const currentDate = new Date(startOfWeek);
      currentDate.setDate(startOfWeek.getDate() + i);
      weekDates.push({
        day: currentDate.toLocaleDateString('en-US', { weekday: 'short' }),
        date: currentDate.getDate(),
        fullDate: new Date(currentDate),
        isToday: currentDate.toDateString() === new Date().toDateString(),
      });
    }
    return weekDates;
  };

  const days = getWeekDates(currentWeek);

  // Fetch calendar events for the current week
  useEffect(() => {
    const fetchEvents = async () => {
      if (!session) return;

      try {
        const startDate = new Date(days[0].fullDate);
        startDate.setHours(0, 0, 0, 0);
        const endDate = new Date(days[6].fullDate);
        endDate.setHours(23, 59, 59, 999);

        const response = await fetch(
          `/api/backend/calendar/events?start_date=${startDate.toISOString()}&end_date=${endDate.toISOString()}`
        );

        if (response.ok) {
          const data = await response.json();
          setEvents(data.events || []);
        }
      } catch (error) {
        console.error('Failed to fetch calendar events:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, [session, currentWeek]);

  // Get events for a specific day
  const getEventsForDay = (dayDate: Date) => {
    return events.filter((event) => {
      const eventDate = new Date(event.start_time);
      return eventDate.toDateString() === dayDate.toDateString();
    });
  };

  const navigateWeek = (direction: 'prev' | 'next') => {
    const newWeek = new Date(currentWeek);
    newWeek.setDate(currentWeek.getDate() + (direction === 'next' ? 7 : -7));
    setCurrentWeek(newWeek);
  };

  const refreshEvents = async () => {
    if (!session) return;

    try {
      const startDate = new Date(days[0].fullDate);
      startDate.setHours(0, 0, 0, 0);
      const endDate = new Date(days[6].fullDate);
      endDate.setHours(23, 59, 59, 999);

      const response = await fetch(
        `/api/backend/calendar/events?start_date=${startDate.toISOString()}&end_date=${endDate.toISOString()}`
      );

      if (response.ok) {
        const data = await response.json();
        setEvents(data.events || []);
      }
    } catch (error) {
      console.error('Failed to fetch calendar events:', error);
    }
  };

  return (
    <Card className="border-2 border-border p-4 shadow-card bg-card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-foreground">This Week</h3>
        <Button variant="ghost" size="sm" className="h-7 text-xs">
          <Check className="h-3 w-3 mr-1" />
          Synced
        </Button>
      </div>

      <div className="flex items-center justify-between mb-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigateWeek('prev')}
          className="h-6 w-6 p-0"
        >
          ←
        </Button>
        <span className="text-xs text-muted-foreground">
          {days[0].fullDate.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
          })}{' '}
          -
          {days[6].fullDate.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
          })}
        </span>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigateWeek('next')}
          className="h-6 w-6 p-0"
        >
          →
        </Button>
      </div>

      <div className="grid grid-cols-7 gap-2 mb-4">
        {days.map((day) => {
          const dayEvents = getEventsForDay(day.fullDate);
          return (
            <div key={day.date} className="flex flex-col items-center">
              <span className="text-xs text-muted-foreground mb-1">
                {day.day}
              </span>
              <button
                className={`w-8 h-8 rounded-full text-sm font-semibold transition-colors relative ${
                  day.isToday
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-muted text-foreground'
                }`}
              >
                {day.date}
                {dayEvents.length > 0 && (
                  <div className="absolute -bottom-1 left-1/2 transform -translate-x-1/2">
                    <div className="w-1 h-1 bg-primary rounded-full"></div>
                  </div>
                )}
              </button>
            </div>
          );
        })}
      </div>

      {/* Show events for today */}
      {(() => {
        const todayEvents = getEventsForDay(new Date());
        return (
          todayEvents.length > 0 && (
            <div className="mb-4">
              <h4 className="text-xs font-medium text-foreground mb-2">
                Today's Events
              </h4>
              <div className="space-y-1">
                {todayEvents.slice(0, 3).map((event) => (
                  <div
                    key={event.id}
                    className="text-xs text-muted-foreground truncate"
                  >
                    {new Date(event.start_time).toLocaleTimeString('en-US', {
                      hour: 'numeric',
                      minute: '2-digit',
                      hour12: true,
                    })}{' '}
                    - {event.title}
                  </div>
                ))}
                {todayEvents.length > 3 && (
                  <div className="text-xs text-muted-foreground">
                    +{todayEvents.length - 3} more
                  </div>
                )}
              </div>
            </div>
          )
        );
      })()}

      <div className="space-y-2">
        <EventCreationModal onEventCreated={refreshEvents} />
        <ClassCreationModal onClassesCreated={refreshEvents} />
      </div>
    </Card>
  );
};

export default WeekCalendar;
