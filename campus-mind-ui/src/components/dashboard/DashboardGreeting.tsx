import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";

interface DashboardGreetingProps {
  userName: string;
  tasksDue: number;
}

const DashboardGreeting = ({ userName, tasksDue }: DashboardGreetingProps) => {
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning";
    if (hour < 18) return "Good afternoon";
    return "Good evening";
  };

  return (
    <div className="relative">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
      <Input
        placeholder="Search topics or notes..."
        className="pl-10 border-2"
      />
    </div>
  );
};

export default DashboardGreeting;
