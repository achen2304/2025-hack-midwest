import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Bell, Settings } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface DashboardHeaderProps {
  userName: string;
  tasksDue: number;
}

const DashboardHeader = ({ userName, tasksDue }: DashboardHeaderProps) => {
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning";
    if (hour < 18) return "Good afternoon";
    return "Good evening";
  };

  return (
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-bold text-foreground">
          {getGreeting()}, {userName}! 👋
        </h1>
        <p className="text-sm text-muted-foreground">
          {tasksDue === 0 ? "No tasks due today. Great job!" : `${tasksDue} tasks due today. You've got this.`}
        </p>
      </div>

      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          <Badge
            variant="destructive"
            className="absolute -top-1 -right-1 h-5 w-5 p-0 flex items-center justify-center text-xs"
          >
            3
          </Badge>
        </Button>

        <Button variant="ghost" size="icon">
          <Settings className="h-5 w-5" />
        </Button>

        <Avatar className="h-9 w-9 border-2 border-primary">
          <AvatarImage src="" alt="User" />
          <AvatarFallback className="bg-primary text-primary-foreground font-semibold">
            SK
          </AvatarFallback>
        </Avatar>
      </div>
    </div>
  );
};

export default DashboardHeader;
