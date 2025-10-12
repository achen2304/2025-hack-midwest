'use client';

import { useState } from 'react';
import { useSession } from 'next-auth/react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Calendar } from '@/components/ui/calendar';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Checkbox } from '@/components/ui/checkbox';
import { CalendarIcon, GraduationCap } from 'lucide-react';
import { format } from 'date-fns';

interface ClassEventCreate {
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  location?: string;
  days_of_week: string[];
  term_start_date: string;
  term_end_date: string;
  priority: 'low' | 'medium' | 'high';
  color?: string;
}

interface ClassCreationModalProps {
  onClassesCreated?: () => void;
}

const ClassCreationModal = ({ onClassesCreated }: ClassCreationModalProps) => {
  const { data: session } = useSession();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [classData, setClassData] = useState<ClassEventCreate>({
    title: '',
    description: '',
    start_time: '',
    end_time: '',
    location: '',
    days_of_week: [],
    term_start_date: '',
    term_end_date: '',
    priority: 'medium',
    color: '#10b981',
  });

  const [termStartDate, setTermStartDate] = useState<Date>();
  const [termEndDate, setTermEndDate] = useState<Date>();
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [selectedDays, setSelectedDays] = useState<string[]>([]);

  const daysOfWeek = [
    { value: 'monday', label: 'Monday' },
    { value: 'tuesday', label: 'Tuesday' },
    { value: 'wednesday', label: 'Wednesday' },
    { value: 'thursday', label: 'Thursday' },
    { value: 'friday', label: 'Friday' },
    { value: 'saturday', label: 'Saturday' },
    { value: 'sunday', label: 'Sunday' },
  ];

  const handleDayToggle = (day: string) => {
    setSelectedDays((prev) =>
      prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (
      !session ||
      !termStartDate ||
      !termEndDate ||
      !startTime ||
      !endTime ||
      selectedDays.length === 0
    )
      return;

    setLoading(true);

    try {
      const response = await fetch('/api/backend/calendar/classes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: classData.title,
          description: classData.description,
          start_time: startTime,
          end_time: endTime,
          location: classData.location,
          days_of_week: selectedDays,
          term_start_date: termStartDate.toISOString(),
          term_end_date: termEndDate.toISOString(),
          priority: classData.priority,
          color: classData.color,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setOpen(false);
        setClassData({
          title: '',
          description: '',
          start_time: '',
          end_time: '',
          location: '',
          days_of_week: [],
          term_start_date: '',
          term_end_date: '',
          priority: 'medium',
          color: '#10b981',
        });
        setTermStartDate(undefined);
        setTermEndDate(undefined);
        setStartTime('');
        setEndTime('');
        setSelectedDays([]);
        onClassesCreated?.();
        alert(`Successfully created ${result.events_created} class events!`);
      }
    } catch (error) {
      console.error('Failed to create class events:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" className="w-full border-2" size="sm">
          <GraduationCap className="h-3 w-3 mr-2" />
          Add Class Schedule
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Create Class Schedule</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="title">Class Title</Label>
            <Input
              id="title"
              value={classData.title}
              onChange={(e) =>
                setClassData({ ...classData, title: e.target.value })
              }
              placeholder="e.g., CS 101 - Introduction to Programming"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={classData.description}
              onChange={(e) =>
                setClassData({ ...classData, description: e.target.value })
              }
              placeholder="Enter class description"
              rows={2}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="location">Location</Label>
            <Input
              id="location"
              value={classData.location}
              onChange={(e) =>
                setClassData({ ...classData, location: e.target.value })
              }
              placeholder="e.g., Room 101, Building A"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Term Start Date</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className="w-full justify-start text-left font-normal"
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {termStartDate
                      ? format(termStartDate, 'PPP')
                      : 'Pick start date'}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="single"
                    selected={termStartDate}
                    onSelect={setTermStartDate}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </div>

            <div className="space-y-2">
              <Label>Term End Date</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className="w-full justify-start text-left font-normal"
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {termEndDate ? format(termEndDate, 'PPP') : 'Pick end date'}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="single"
                    selected={termEndDate}
                    onSelect={setTermEndDate}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="startTime">Start Time</Label>
              <Input
                id="startTime"
                type="time"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="endTime">End Time</Label>
              <Input
                id="endTime"
                type="time"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label>Days of Week</Label>
            <div className="grid grid-cols-2 gap-2">
              {daysOfWeek.map((day) => (
                <div key={day.value} className="flex items-center space-x-2">
                  <Checkbox
                    id={day.value}
                    checked={selectedDays.includes(day.value)}
                    onCheckedChange={() => handleDayToggle(day.value)}
                  />
                  <Label htmlFor={day.value} className="text-sm font-normal">
                    {day.label}
                  </Label>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="priority">Priority</Label>
            <Select
              value={classData.priority}
              onValueChange={(value) =>
                setClassData({ ...classData, priority: value as any })
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="low">Low</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="high">High</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex justify-end space-x-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={loading || selectedDays.length === 0}
            >
              {loading ? 'Creating...' : 'Create Class Schedule'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default ClassCreationModal;
