'use client';

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Clock, Edit, CheckCircle, Plus, Calendar } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useToast } from '@/hooks/use-toast';
import { useSession } from 'next-auth/react';
import EventCreationModal from './EventCreationModal';
import ClassCreationModal from './ClassCreationModal';

interface StudyBlock {
  id: string;
  time: string;
  title: string;
  duration: string;
  event_type: string;
  start_time: string;
  end_time: string;
}

const TodayStudyPlan = () => {
  const { toast } = useToast();
  const { data: session } = useSession();
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [blocks, setBlocks] = useState<StudyBlock[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch today's study blocks from calendar events
  useEffect(() => {
    const fetchTodayEvents = async () => {
      if (!session) return;

      try {
        const today = new Date();
        const startOfDay = new Date(today);
        startOfDay.setHours(0, 0, 0, 0);
        const endOfDay = new Date(today);
        endOfDay.setHours(23, 59, 59, 999);

        const response = await fetch(
          `/api/backend/calendar/events?start_date=${startOfDay.toISOString()}&end_date=${endOfDay.toISOString()}&event_type=STUDY_BLOCK`
        );

        if (response.ok) {
          const data = await response.json();
          const studyBlocks = (data.events || []).map((event: any) => ({
            id: event.id,
            time: new Date(event.start_time).toLocaleTimeString('en-US', {
              hour: 'numeric',
              minute: '2-digit',
              hour12: true,
            }),
            title: event.title,
            duration: calculateDuration(event.start_time, event.end_time),
            event_type: event.event_type,
            start_time: event.start_time,
            end_time: event.end_time,
          }));
          setBlocks(studyBlocks);
        }
      } catch (error) {
        console.error("Failed to fetch today's study blocks:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchTodayEvents();
  }, [session]);

  const calculateDuration = (startTime: string, endTime: string) => {
    const start = new Date(startTime);
    const end = new Date(endTime);
    const diffMs = end.getTime() - start.getTime();
    const diffMins = Math.round(diffMs / (1000 * 60));

    if (diffMins < 60) {
      return `${diffMins} min`;
    } else {
      const hours = Math.floor(diffMins / 60);
      const mins = diffMins % 60;
      return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
    }
  };

  const handleRegenerate = () => {
    setIsRegenerating(true);
    setTimeout(() => {
      setIsRegenerating(false);
      toast({
        title: 'Study plan regenerated',
        description: 'Your schedule has been optimized with AI',
      });
    }, 1500);
  };

  const refreshStudyBlocks = async () => {
    if (!session) return;

    try {
      const today = new Date();
      const startOfDay = new Date(today);
      startOfDay.setHours(0, 0, 0, 0);
      const endOfDay = new Date(today);
      endOfDay.setHours(23, 59, 59, 999);

      const response = await fetch(
        `/api/backend/calendar/events?start_date=${startOfDay.toISOString()}&end_date=${endOfDay.toISOString()}&event_type=STUDY_BLOCK`
      );

      if (response.ok) {
        const data = await response.json();
        const studyBlocks = (data.events || []).map((event: any) => ({
          id: event.id,
          time: new Date(event.start_time).toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true,
          }),
          title: event.title,
          duration: calculateDuration(event.start_time, event.end_time),
          event_type: event.event_type,
          start_time: event.start_time,
          end_time: event.end_time,
        }));
        setBlocks(studyBlocks);
      }
    } catch (error) {
      console.error("Failed to fetch today's study blocks:", error);
    }
  };

  if (loading) {
    return (
      <Card className="border-2 border-border p-6 shadow-card bg-card">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-foreground">
              Today&apos;s Study Plan
            </h3>
            <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
              <Calendar className="h-3 w-3" />
              Loading study blocks...
            </p>
          </div>
        </div>
        <div className="text-center py-8 text-muted-foreground">
          Loading your study plan...
        </div>
      </Card>
    );
  }

  return (
    <Card className="border-2 border-border p-6 shadow-card bg-card">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-foreground">
            Today&apos;s Study Plan
          </h3>
          <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
            <Calendar className="h-3 w-3" />
            {blocks.length > 0
              ? `${blocks.length} study block${
                  blocks.length !== 1 ? 's' : ''
                } scheduled`
              : 'No study blocks scheduled for today'}
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleRegenerate}
          disabled={isRegenerating}
          className="border-2"
        >
          {isRegenerating ? 'Regenerating...' : 'Regenerate with AI'}
        </Button>
      </div>

      <div className="space-y-3">
        {blocks.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <Calendar className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p className="text-sm">No study blocks scheduled for today</p>
            <p className="text-xs mt-1">
              Add events below to create your study plan
            </p>
          </div>
        ) : (
          blocks.map((block) => (
            <div
              key={block.id}
              className="flex items-center gap-3 p-4 rounded-lg border-2 border-border bg-card hover:bg-muted/50 transition-colors"
            >
              <Clock className="h-4 w-4 text-muted-foreground flex-shrink-0" />
              <span className="text-sm font-semibold text-foreground w-20 flex-shrink-0">
                {block.time}
              </span>
              <div className="flex-1">
                <p className="text-sm font-medium text-foreground">
                  {block.title}
                </p>
                <p className="text-xs text-muted-foreground">
                  {block.duration}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <Edit className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <CheckCircle className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))
        )}

        <div className="space-y-2">
          <EventCreationModal onEventCreated={refreshStudyBlocks} />
          <ClassCreationModal onClassesCreated={refreshStudyBlocks} />
        </div>
      </div>
    </Card>
  );
};

export default TodayStudyPlan;
