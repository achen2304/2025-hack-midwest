'use client';

import { Card } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { CheckCircle2 } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';

interface Assignment {
  id: string;
  name: string;
  description?: string;
  due_at: string;
  course_id: string;
  points_possible?: number;
  submission_types: string[];
  status: 'not_started' | 'in_progress' | 'completed';
  canvas_workflow_state?: string;
}

const TasksAssignments = () => {
  const { data: session } = useSession();
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch assignments from the backend
useEffect(() => {
    const fetchAssignments = async () => {
      if (!session) return;

      try {
        const response = await fetch('/api/backend/assignments');

        if (response.ok) {
          const data = await response.json();
          setAssignments(data || []);
        }
      } catch (error) {
        console.error('Failed to fetch assignments:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAssignments();
  }, [session]);

  const updateAssignmentStatus = async (
    assignmentId: string,
    newStatus: string
  ) => {
    if (!session) return;

    try {
      const response = await fetch(
        `/api/backend/assignments/${assignmentId}/status`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ status: newStatus }),
        }
      );

      if (response.ok) {
        // Update local state
        setAssignments((prev) =>
          prev.map((assignment) =>
            assignment.id === assignmentId
              ? {
                  ...assignment,
                  status: newStatus as
                    | 'not_started'
                    | 'in_progress'
                    | 'completed',
                }
              : assignment
          )
        );
      }
    } catch (error) {
      console.error('Failed to update assignment status:', error);
    }
  };

  const toggleTask = (assignmentId: string, currentStatus: string) => {
    const newStatus =
      currentStatus === 'completed' ? 'not_started' : 'completed';
    updateAssignmentStatus(assignmentId, newStatus);
  };

  const getPriorityVariant = (dueDate: string) => {
    const due = new Date(dueDate);
    const now = new Date();
    const diffDays = Math.ceil(
      (due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)
    );

    if (diffDays <= 1) return 'destructive';
    if (diffDays <= 3) return 'default';
    return 'secondary';
  };

  const getPriorityLabel = (dueDate: string) => {
    const due = new Date(dueDate);
    const now = new Date();
    const diffDays = Math.ceil(
      (due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)
    );

    if (diffDays <= 0) return 'overdue';
    if (diffDays <= 1) return 'high';
    if (diffDays <= 3) return 'medium';
    return 'low';
  };

  const formatDueDate = (dueDate: string) => {
    const due = new Date(dueDate);
    const now = new Date();
    const diffDays = Math.ceil(
      (due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)
    );

    if (diffDays < 0) return 'Overdue';
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Tomorrow';
    if (diffDays <= 7)
      return due.toLocaleDateString('en-US', { weekday: 'long' });
    return due.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  // Filter assignments for different tabs
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(today.getDate() + 1);

  const todayTasks = assignments.filter((assignment) => {
    const due = new Date(assignment.due_at);
    return due.toDateString() === today.toDateString();
  });

  const weekTasks = assignments.filter((assignment) => {
    const due = new Date(assignment.due_at);
    const weekFromNow = new Date(today);
    weekFromNow.setDate(today.getDate() + 7);
    return (
      due >= today && due <= weekFromNow && assignment.status !== 'completed'
    );
  });

  const allTasks = assignments;

  const renderTask = (assignment: Assignment) => (
    <div
      key={assignment.id}
      className="flex items-start gap-3 p-4 rounded-lg border-2 border-border bg-card hover:bg-muted/50 transition-colors"
    >
      <Checkbox
        checked={assignment.status === 'completed'}
        onCheckedChange={() => toggleTask(assignment.id, assignment.status)}
        className="mt-1"
      />
      <div className="flex-1 min-w-0">
        <p
          className={`text-sm font-medium ${
            assignment.status === 'completed'
              ? 'line-through text-muted-foreground'
              : 'text-foreground'
          }`}
        >
          {assignment.name}
        </p>
        <p className="text-xs text-muted-foreground mt-1">
          {assignment.course_id} • {formatDueDate(assignment.due_at)}
          {assignment.points_possible && ` • ${assignment.points_possible} pts`}
        </p>
        {assignment.description && (
          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
            {assignment.description}
          </p>
        )}
      </div>
      <Badge
        variant={getPriorityVariant(assignment.due_at)}
        className="text-xs flex-shrink-0"
      >
        {getPriorityLabel(assignment.due_at)}
      </Badge>
    </div>
  );

  if (loading) {
    return (
      <Card className="border-2 border-border p-6 shadow-card bg-card">
        <div className="flex items-center gap-2 mb-4">
          <CheckCircle2 className="h-5 w-5 text-primary" />
          <h3 className="text-lg font-semibold text-foreground">
            Tasks & Assignments
          </h3>
        </div>
        <div className="text-center py-8 text-muted-foreground">
          Loading assignments...
        </div>
      </Card>
    );
  }

  return (
    <Card className="border-2 border-border p-6 shadow-card bg-card">
      <div className="flex items-center gap-2 mb-4">
        <CheckCircle2 className="h-5 w-5 text-primary" />
        <h3 className="text-lg font-semibold text-foreground">
          Tasks & Assignments
        </h3>
      </div>

      <Tabs defaultValue="today" className="w-full">
        <TabsList className="grid w-full grid-cols-3 mb-4">
          <TabsTrigger value="today">
            Due Today ({todayTasks.length})
          </TabsTrigger>
          <TabsTrigger value="week">This Week ({weekTasks.length})</TabsTrigger>
          <TabsTrigger value="all">All Tasks ({allTasks.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="today" className="space-y-3 mt-0">
          {todayTasks.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No assignments due today! 🎉
            </div>
          ) : (
            <>
              {todayTasks
                .filter((t) => t.status !== 'completed')
                .map(renderTask)}
              {todayTasks.filter((t) => t.status === 'completed').length >
                0 && (
                <>
                  <div className="border-t border-border my-4"></div>
                  <div className="text-xs text-muted-foreground mb-2">
                    Completed today:
                  </div>
                  {todayTasks
                    .filter((t) => t.status === 'completed')
                    .map(renderTask)}
                </>
              )}
            </>
          )}
        </TabsContent>

        <TabsContent value="week" className="space-y-3 mt-0">
          {weekTasks.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No assignments due this week! 🎉
            </div>
          ) : (
            weekTasks.map(renderTask)
          )}
        </TabsContent>

        <TabsContent value="all" className="space-y-3 mt-0">
          {allTasks.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No assignments found. Sync with Canvas to see your assignments.
            </div>
          ) : (
            <>
              {allTasks.filter((t) => t.status !== 'completed').map(renderTask)}
              {allTasks.filter((t) => t.status === 'completed').length > 0 && (
                <>
                  <div className="border-t border-border my-4"></div>
                  <div className="text-xs text-muted-foreground mb-2">
                    Completed assignments:
                  </div>
                  {allTasks
                    .filter((t) => t.status === 'completed')
                    .map(renderTask)}
                </>
              )}
            </>
          )}
        </TabsContent>
      </Tabs>
    </Card>
  );
};

export default TasksAssignments;
