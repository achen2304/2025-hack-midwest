'use client';

import { Card } from '@/components/ui/card';
import { BookOpen, Brain, Heart, Calendar } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';

interface Assignment {
  id: string;
  name: string;
  due_at: string;
  course_id: string;
  status: string;
}

interface CalendarEvent {
  id: string;
  title: string;
  start_time: string;
  end_time: string;
  event_type: string;
}

const QuickStatsCards = () => {
  const { data: session } = useSession();
  const [activeCourse, setActiveCourse] = useState<{
    course_id: string;
    nextDue: string;
    daysUntil: number;
  } | null>(null);
  const [studySessions, setStudySessions] = useState<number>(0);
  const [loading, setLoading] = useState(true);

  // Fetch active course (course with closest due date)
  useEffect(() => {
    const fetchActiveCourse = async () => {
      if (!session) return;

      try {
        const response = await fetch('/api/backend/assignments?weeks=4');
        if (response.ok) {
          const assignments: Assignment[] = await response.json();

          // Filter for incomplete assignments and find the one due soonest
          const incompleteAssignments = assignments.filter(
            (assignment) => assignment.status !== 'completed'
          );

          if (incompleteAssignments.length > 0) {
            // Sort by due date and get the closest one
            const sortedAssignments = incompleteAssignments.sort(
              (a, b) =>
                new Date(a.due_at).getTime() - new Date(b.due_at).getTime()
            );

            const closestAssignment = sortedAssignments[0];
            const dueDate = new Date(closestAssignment.due_at);
            const now = new Date();
            const diffTime = dueDate.getTime() - now.getTime();
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

            setActiveCourse({
              course_id: closestAssignment.course_id,
              nextDue: closestAssignment.name,
              daysUntil: diffDays,
            });
          }
        }
      } catch (error) {
        console.error('Failed to fetch active course:', error);
      }
    };

    fetchActiveCourse();
  }, [session]);

  // Fetch study sessions for the week
  useEffect(() => {
    const fetchStudySessions = async () => {
      if (!session) return;

      try {
        const now = new Date();
        const startOfWeek = new Date(now);
        startOfWeek.setDate(now.getDate() - now.getDay()); // Start of week (Sunday)
        startOfWeek.setHours(0, 0, 0, 0);

        const endOfWeek = new Date(startOfWeek);
        endOfWeek.setDate(startOfWeek.getDate() + 6); // End of week (Saturday)
        endOfWeek.setHours(23, 59, 59, 999);

        const response = await fetch(
          `/api/backend/calendar/events?start_date=${startOfWeek.toISOString()}&end_date=${endOfWeek.toISOString()}&event_type=STUDY_BLOCK`
        );

        if (response.ok) {
          const data = await response.json();
          const studyBlocks: CalendarEvent[] = data.events || [];
          setStudySessions(studyBlocks.length);
        }
      } catch (error) {
        console.error('Failed to fetch study sessions:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStudySessions();
  }, [session]);

  const formatDueText = (daysUntil: number) => {
    if (daysUntil < 0) return 'Overdue';
    if (daysUntil === 0) return 'Due today';
    if (daysUntil === 1) return 'Due tomorrow';
    return `Due in ${daysUntil} days`;
  };

  const stats = [
    {
      icon: BookOpen,
      label: 'Active Course',
      value: activeCourse?.course_id || 'None',
      subtext: activeCourse
        ? formatDueText(activeCourse.daysUntil)
        : 'No upcoming assignments',
      color: 'text-primary',
    },
    {
      icon: Brain,
      label: 'Study Sessions',
      value: `${studySessions} sessions`,
      subtext: 'This week',
      color: 'text-accent',
    },
    {
      icon: Heart,
      label: 'Wellness',
      value: 'Focused',
      subtext: 'Keep up the pace!',
      color: 'text-success',
    },
    {
      icon: Calendar,
      label: 'Upcoming',
      value: activeCourse?.course_id || 'None',
      subtext: activeCourse?.nextDue || 'No upcoming events',
      color: 'text-primary',
    },
  ];

  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <Card
            key={index}
            className="border-2 border-border p-4 shadow-card bg-card"
          >
            <div className="flex items-start gap-3">
              <div className="h-5 w-5 bg-muted rounded animate-pulse mt-0.5" />
              <div className="flex-1 min-w-0">
                <div className="h-3 bg-muted rounded animate-pulse mb-1" />
                <div className="h-5 bg-muted rounded animate-pulse mb-1" />
                <div className="h-3 bg-muted rounded animate-pulse" />
              </div>
            </div>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <Card
          key={stat.label}
          className="border-2 border-border p-4 shadow-card bg-card"
        >
          <div className="flex items-start gap-3">
            <stat.icon className={`h-5 w-5 ${stat.color} mt-0.5`} />
            <div className="flex-1 min-w-0">
              <p className="text-xs text-muted-foreground mb-1">{stat.label}</p>
              <p className="text-lg font-bold text-foreground truncate">
                {stat.value}
              </p>
              <p className="text-xs text-muted-foreground">{stat.subtext}</p>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
};

export default QuickStatsCards;
