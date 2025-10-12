'use client';

import { useState } from 'react';
import { useSession } from 'next-auth/react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from '@/components/ui/dialog';
import { Calendar } from '@/components/ui/calendar';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { CalendarIcon, Sparkles, Loader2 } from 'lucide-react';
import { format, addDays } from 'date-fns';

interface AIScheduleRegeneratorProps {
  onScheduleGenerated?: () => void;
  variant?: 'default' | 'outline' | 'ghost';
  size?: 'default' | 'sm' | 'lg';
  fullWidth?: boolean;
}

const AIScheduleRegenerator = ({
  onScheduleGenerated,
  variant = 'default',
  size = 'default',
  fullWidth = false
}: AIScheduleRegeneratorProps) => {
  const { data: session } = useSession();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [startDate, setStartDate] = useState<Date>(new Date());
  const [endDate, setEndDate] = useState<Date>(addDays(new Date(), 14)); // Default 2 weeks
  const [prioritizeCourses, setPrioritizeCourses] = useState<string>('');
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleGenerate = async () => {
    if (!session) return;

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch('/api/backend/schedule/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          regenerate: true, // Always regenerate (clear old AI blocks)
          start_date: startDate.toISOString(),
          end_date: endDate.toISOString(),
          prioritize_courses: prioritizeCourses
            ? prioritizeCourses.split(',').map(c => c.trim()).filter(c => c)
            : [],
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setResult({
          success: true,
          message: data.message || 'Schedule generated successfully!',
        });
        setTimeout(() => {
          setOpen(false);
          setResult(null);
          onScheduleGenerated?.();
        }, 2000);
      } else {
        setResult({
          success: false,
          message: data.detail || 'Failed to generate schedule',
        });
      }
    } catch (error) {
      console.error('Failed to generate schedule:', error);
      setResult({
        success: false,
        message: 'Network error. Please try again.',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          variant={variant}
          size={size}
          className={fullWidth ? 'w-full' : ''}
        >
          <Sparkles className="h-4 w-4 mr-2" />
          Generate AI Schedule
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            Generate AI Study Schedule
          </DialogTitle>
          <DialogDescription>
            Let AI create an optimized study schedule based on your assignments, classes, and preferences.
            This will replace any existing AI-generated study blocks.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Start Date</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className="w-full justify-start text-left font-normal"
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {format(startDate, 'PPP')}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="single"
                    selected={startDate}
                    onSelect={(date) => date && setStartDate(date)}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </div>

            <div className="space-y-2">
              <Label>End Date</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className="w-full justify-start text-left font-normal"
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {format(endDate, 'PPP')}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="single"
                    selected={endDate}
                    onSelect={(date) => date && setEndDate(date)}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="prioritize">
              Prioritize Courses (optional)
            </Label>
            <Input
              id="prioritize"
              placeholder="e.g., CS101, MATH202 (comma-separated course IDs)"
              value={prioritizeCourses}
              onChange={(e) => setPrioritizeCourses(e.target.value)}
            />
            <p className="text-xs text-muted-foreground">
              Enter course IDs separated by commas to allocate more study time to them
            </p>
          </div>

          {result && (
            <div
              className={`p-3 rounded-lg border-2 ${
                result.success
                  ? 'bg-green-50 border-green-200 text-green-800'
                  : 'bg-red-50 border-red-200 text-red-800'
              }`}
            >
              <p className="text-sm font-medium">{result.message}</p>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={() => setOpen(false)}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button onClick={handleGenerate} disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                Generate Schedule
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default AIScheduleRegenerator;
