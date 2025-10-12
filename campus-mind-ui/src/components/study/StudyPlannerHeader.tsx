import { RefreshCw, Link2, Flame } from "lucide-react";
import { Button } from "@/components/ui/button";

const StudyPlannerHeader = () => {
  return (
    <div className="flex items-start justify-between mb-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Study Planner</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Generate a personalized study plan and let CampusMind help you prepare smarter.
        </p>
      </div>
      <div className="flex items-center gap-2">
        <Button variant="outline" size="sm" className="gap-2">
          <Link2 className="h-4 w-4" />
          Sync Canvas
        </Button>
        <Button variant="ghost" size="icon">
          <RefreshCw className="h-4 w-4" />
        </Button>
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-orange-500/10 to-red-500/10 border border-orange-500/20">
          <Flame className="h-4 w-4 text-orange-500" />
          <span className="text-sm font-semibold text-orange-500">7</span>
        </div>
      </div>
    </div>
  );
};

export default StudyPlannerHeader;
