import DashboardHeader from "@/components/dashboard/DashboardHeader";
import DashboardGreeting from "@/components/dashboard/DashboardGreeting";
import QuickStatsCards from "@/components/dashboard/QuickStatsCards";
import TodayStudyPlan from "@/components/dashboard/TodayStudyPlan";
import TasksAssignments from "@/components/dashboard/TasksAssignments";
import WeekCalendar from "@/components/dashboard/WeekCalendar";
import UpcomingEventsList from "@/components/dashboard/UpcomingEventsList";
import AIRecommendations from "@/components/dashboard/AIRecommendations";

const Today = () => {
  return (
    <div className="min-h-screen">
      <DashboardHeader userName="Hemanth" tasksDue={3} />

      <div className="mt-6 space-y-6">
        <DashboardGreeting userName="Hemanth" tasksDue={3} />
        
        <QuickStatsCards />

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-6">
          {/* Main Content */}
          <div className="space-y-6">
            <TodayStudyPlan />
            <TasksAssignments />
          </div>

          {/* Right Sidebar */}
          <div className="space-y-6">
            <WeekCalendar />
            <UpcomingEventsList />
            <AIRecommendations />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Today;
