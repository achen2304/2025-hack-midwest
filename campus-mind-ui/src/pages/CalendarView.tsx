'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import AIScheduleRegenerator from '@/components/dashboard/AIScheduleRegenerator';
import {
  format,
  startOfWeek,
  endOfWeek,
  eachDayOfInterval,
  addWeeks,
  subWeeks,
  isSameDay,
  startOfMonth,
  endOfMonth,
  addMonths,
  subMonths,
  getDay,
  isSameMonth,
} from 'date-fns';

interface CalendarEvent {
  id: string;
  title: string;
  date: Date;
  type: 'assignment' | 'quiz' | 'exam' | 'event';
  course?: string;
  time?: string;
}

const CalendarView = () => {
  const [viewMode, setViewMode] = useState<'week' | 'month'>('week');
  const [currentDate, setCurrentDate] = useState(new Date(2025, 9, 12)); // Oct 12, 2025

  // Mock data - replace with actual data from Canvas and Google Calendar
  const events: CalendarEvent[] = [
    {
      id: '1',
      title: 'CS 101 Assignment',
      date: new Date(2025, 9, 13),
      type: 'assignment',
      course: 'CS 101',
      time: '11:59 PM',
    },
    {
      id: '2',
      title: 'Math Quiz',
      date: new Date(2025, 9, 14),
      type: 'quiz',
      course: 'MATH 201',
      time: '2:00 PM',
    },
    {
      id: '3',
      title: 'Physics Midterm',
      date: new Date(2025, 9, 15),
      type: 'exam',
      course: 'PHYS 150',
      time: '10:00 AM',
    },
    {
      id: '4',
      title: 'Team Meeting',
      date: new Date(2025, 9, 15),
      type: 'event',
      time: '3:00 PM',
    },
    {
      id: '5',
      title: 'Lab Report Due',
      date: new Date(2025, 9, 16),
      type: 'assignment',
      course: 'CHEM 101',
      time: '11:59 PM',
    },
    {
      id: '6',
      title: 'Study Group',
      date: new Date(2025, 9, 17),
      type: 'event',
      time: '6:00 PM',
    },
  ];

  const getWeekDays = () => {
    const start = startOfWeek(currentDate, { weekStartsOn: 0 });
    const end = endOfWeek(currentDate, { weekStartsOn: 0 });
    return eachDayOfInterval({ start, end });
  };

  const getMonthDays = () => {
    const start = startOfMonth(currentDate);
    const end = endOfMonth(currentDate);
    const days = eachDayOfInterval({ start, end });

    // Add padding days for calendar grid
    const startDay = getDay(start);
    const paddingStart = Array(startDay).fill(null);

    return [...paddingStart, ...days];
  };

  const getEventsForDay = (day: Date) => {
    return events.filter((event) => isSameDay(event.date, day));
  };

  const getTypeColor = (type: CalendarEvent['type']) => {
    switch (type) {
      case 'assignment':
        return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300';
      case 'quiz':
        return 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300';
      case 'exam':
        return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300';
      case 'event':
        return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300';
    }
  };

  const getEventDotColor = (type: CalendarEvent['type']) => {
    switch (type) {
      case 'assignment':
        return 'bg-blue-500';
      case 'quiz':
        return 'bg-purple-500';
      case 'exam':
        return 'bg-red-500';
      case 'event':
        return 'bg-green-500';
    }
  };

  const getTypeBadgeColor = (type: CalendarEvent['type']) => {
    switch (type) {
      case 'assignment':
        return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300';
      case 'quiz':
        return 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300';
      case 'exam':
        return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300';
      case 'event':
        return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300';
    }
  };

  const navigateWeek = (direction: 'prev' | 'next') => {
    setCurrentDate(
      direction === 'prev' ? subWeeks(currentDate, 1) : addWeeks(currentDate, 1)
    );
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentDate(
      direction === 'prev'
        ? subMonths(currentDate, 1)
        : addMonths(currentDate, 1)
    );
  };

  return (
    <Card className="border-2 border-foreground bg-background p-8 rounded-3xl">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-foreground mb-1">Calendar</h1>
          <p className="text-sm text-muted-foreground">
            {viewMode === 'week'
              ? `Week of ${format(
                  startOfWeek(currentDate, { weekStartsOn: 0 }),
                  'MMM d, yyyy'
                )}`
              : format(currentDate, 'MMMM yyyy')}
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* AI Schedule Regenerator */}
          <AIScheduleRegenerator
            onScheduleGenerated={() => {
              // Refresh calendar data when schedule is generated
              console.log('Schedule generated, refreshing calendar...');
            }}
            variant="outline"
            size="sm"
          />

          {/* View Toggle */}
          <div className="flex rounded-full border-2 border-foreground p-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setViewMode('week')}
              className={`rounded-full px-6 ${
                viewMode === 'week'
                  ? 'bg-primary text-primary-foreground hover:bg-primary hover:text-primary-foreground'
                  : 'hover:bg-transparent'
              }`}
            >
              Week
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setViewMode('month')}
              className={`rounded-full px-6 ${
                viewMode === 'month'
                  ? 'bg-primary text-primary-foreground hover:bg-primary hover:text-primary-foreground'
                  : 'hover:bg-transparent'
              }`}
            >
              Month
            </Button>
          </div>

          {/* Navigation */}
          <Button
            variant="outline"
            size="icon"
            onClick={() =>
              viewMode === 'week' ? navigateWeek('prev') : navigateMonth('prev')
            }
            className="h-10 w-10 rounded-full border-2 border-foreground"
          >
            <ChevronLeft className="h-5 w-5" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentDate(new Date(2025, 9, 12))}
            className="h-10 px-6 rounded-full border-2 border-foreground"
          >
            Today
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={() =>
              viewMode === 'week' ? navigateWeek('next') : navigateMonth('next')
            }
            className="h-10 w-10 rounded-full border-2 border-foreground"
          >
            <ChevronRight className="h-5 w-5" />
          </Button>
        </div>
      </div>

      {/* Week View */}
      {viewMode === 'week' && (
        <div className="space-y-4">
          <div className="grid grid-cols-7 gap-3">
            {getWeekDays().map((day) => {
              const dayEvents = getEventsForDay(day);
              const isToday = isSameDay(day, new Date(2025, 9, 12));

              return (
                <div key={day.toString()}>
                  {/* Day Header */}
                  <div
                    className={`mb-3 rounded-3xl p-4 text-center border-2 border-foreground ${
                      isToday
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted'
                    }`}
                  >
                    <div className="text-sm font-semibold mb-1">
                      {format(day, 'EEE')}
                    </div>
                    <div className="text-3xl font-bold">{format(day, 'd')}</div>
                  </div>

                  {/* Events */}
                  <div className="space-y-2">
                    {dayEvents.map((event) => (
                      <div
                        key={event.id}
                        className={`rounded-2xl border-2 border-foreground p-3 shadow-card ${getTypeColor(
                          event.type
                        )}`}
                      >
                        <p className="font-bold text-sm mb-1">{event.title}</p>
                        <p className="text-xs font-medium">{event.time}</p>
                        {event.course && (
                          <p className="text-xs font-medium mt-0.5">
                            {event.course}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Month View */}
      {viewMode === 'month' && (
        <div className="space-y-6">
          {/* Calendar Grid */}
          <Card className="border-2 border-foreground bg-background p-6 rounded-3xl shadow-card">
            {/* Month Navigation */}
            <div className="mb-6 flex items-center justify-between">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => navigateMonth('prev')}
                className="h-10 w-10 rounded-full border-2 border-foreground hover:bg-muted"
              >
                <ChevronLeft className="h-5 w-5" />
              </Button>

              <h2 className="text-2xl font-bold text-foreground">
                {format(currentDate, 'MMMM yyyy')}
              </h2>

              <Button
                variant="ghost"
                size="icon"
                onClick={() => navigateMonth('next')}
                className="h-10 w-10 rounded-full border-2 border-foreground hover:bg-muted"
              >
                <ChevronRight className="h-5 w-5" />
              </Button>
            </div>

            {/* Calendar Grid */}
            <div className="grid grid-cols-7 gap-3">
              {/* Day Headers */}
              {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
                <div
                  key={day}
                  className="text-center text-sm font-semibold text-foreground py-2"
                >
                  {day}
                </div>
              ))}

              {/* Calendar Days */}
              {getMonthDays().map((day, index) => {
                if (!day) {
                  return (
                    <div
                      key={`empty-${index}`}
                      className="aspect-square rounded-3xl border-2 border-foreground bg-background"
                    />
                  );
                }

                const dayEvents = getEventsForDay(day);
                const isSelected = isSameDay(day, currentDate);
                const isToday = isSameDay(day, new Date(2025, 9, 12));
                const isCurrentMonth = isSameMonth(day, currentDate);

                return (
                  <div
                    key={day.toString()}
                    onClick={() => setCurrentDate(day)}
                    className={`
                      aspect-square rounded-3xl border-2 border-foreground p-3 cursor-pointer transition-all bg-background hover:bg-muted/40
                      ${isToday ? 'bg-yellow-300 dark:bg-yellow-400' : ''}
                      ${!isCurrentMonth ? 'opacity-40' : ''}
                    `}
                  >
                    <div className="text-base font-bold mb-2 text-foreground">
                      {format(day, 'd')}
                    </div>

                    {/* Event List */}
                    <div className="space-y-1 text-[10px]">
                      {dayEvents.slice(0, 2).map((event) => {
                        const eventColor =
                          event.type === 'assignment'
                            ? 'text-blue-600'
                            : event.type === 'quiz'
                            ? 'text-purple-600'
                            : event.type === 'exam'
                            ? 'text-red-600'
                            : 'text-green-600';

                        return (
                          <div
                            key={event.id}
                            className="flex items-start gap-1"
                          >
                            <div
                              className={`h-1.5 w-1.5 rounded-full flex-shrink-0 mt-0.5 ${getEventDotColor(
                                event.type
                              )}`}
                            />
                            <span
                              className={`truncate font-semibold leading-tight ${eventColor}`}
                            >
                              {event.time} {event.title}
                            </span>
                          </div>
                        );
                      })}
                      {dayEvents.length > 2 && (
                        <div className="text-[10px] font-medium text-muted-foreground pl-2.5">
                          +{dayEvents.length - 2} more
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>

          {/* Events List for Selected Day */}
          <div className="space-y-3">
            <h3 className="text-xl font-bold text-foreground">
              Events for {format(currentDate, 'MMMM d, yyyy')}
            </h3>

            {getEventsForDay(currentDate).length > 0 ? (
              <div className="space-y-3">
                {getEventsForDay(currentDate).map((event) => (
                  <Card
                    key={event.id}
                    className="border-2 border-foreground bg-background p-5 rounded-3xl shadow-card hover:shadow-card-hover transition-all"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1">
                        <p className="font-bold text-lg text-foreground">
                          {event.title}
                        </p>
                        {event.course && (
                          <p className="mt-1 text-sm text-muted-foreground">
                            {event.course}
                          </p>
                        )}
                        {event.time && (
                          <p className="mt-0.5 text-sm text-muted-foreground">
                            {event.time}
                          </p>
                        )}
                      </div>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${getTypeBadgeColor(
                          event.type
                        )}`}
                      >
                        {event.type}
                      </span>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <Card className="border-2 border-dashed border-foreground bg-muted/20 p-8 rounded-3xl shadow-card">
                <p className="text-center text-muted-foreground">
                  No events scheduled for this day
                </p>
              </Card>
            )}
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="mt-8 flex flex-wrap gap-4 border-t-2 border-foreground pt-6">
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded-full bg-blue-500" />
          <span className="text-sm font-medium text-foreground">
            Assignment
          </span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded-full bg-purple-500" />
          <span className="text-sm font-medium text-foreground">Quiz</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded-full bg-red-500" />
          <span className="text-sm font-medium text-foreground">Exam</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded-full bg-green-500" />
          <span className="text-sm font-medium text-foreground">Event</span>
        </div>
      </div>
    </Card>
  );
};

export default CalendarView;
