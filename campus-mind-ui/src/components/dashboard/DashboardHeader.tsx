"use client"

import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator } from "@/components/ui/dropdown-menu";
import { Bell, Settings, LogOut, User as UserIcon } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { signOut } from "next-auth/react";
import { redirect } from "next/dist/server/api-utils";
import { useRouter } from "next/navigation";

interface DashboardHeaderProps {
  userImage: string;
  userEmail: string;
  userName: string;
  tasksDue: number;
}

const DashboardHeader = ({ userImage, userEmail, userName, tasksDue }: DashboardHeaderProps) => {
  const router = useRouter();

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning";
    if (hour < 18) return "Good afternoon";
    return "Good evening";
  };

  function initials(fullName: string): string {
  if (!fullName) {
    return ''; // Handle empty or null names gracefully
  }

  const nameParts = fullName.split(' ').filter(part => part.length > 0); // Split by space and remove empty strings
  let initials = '';

  for (const part of nameParts) {
    initials += part[0].toUpperCase(); // Take the first letter and capitalize it
  }

  return initials;
}

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

      {/* Avatar menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button
              className="rounded-full focus:outline-none focus:ring-2 focus:ring-primary/40"
              aria-label="User menu"
            >
              <Avatar className="h-9 w-9 border-2 border-primary">
                <AvatarImage src={userImage ?? ""} alt={userName || "User"} />
                <AvatarFallback className="bg-primary text-primary-foreground font-semibold">
                  {initials(userName)}
                </AvatarFallback>
              </Avatar>
            </button>
          </DropdownMenuTrigger>

          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuLabel className="flex flex-col">
              <span className="font-medium">{userName || "User"}</span>
              {userEmail && <span className="text-xs text-muted-foreground truncate">{userEmail}</span>}
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => router.push("/dashboard/settings")} className="cursor-pointer">
              <Settings className="mr-2 h-4 w-4" />
              <span>Settings</span>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => signOut({ callbackUrl: "/" })}
              className="cursor-pointer text-red-600 focus:text-red-600"
            >
              <LogOut className="mr-2 h-4 w-4" />
              <span>Log out</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
};

export default DashboardHeader;
