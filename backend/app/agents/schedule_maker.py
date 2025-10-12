"""
Schedule Maker Agent - Creates and maintains dynamic study schedules
"""
from typing import List, Dict, Any
from strands import Agent
from strands.models import BedrockModel
import json


class ScheduleMakerAgent:
    """
    AI agent that creates and maintains dynamic study schedules.
    - Schedules study blocks around deadlines
    - Respects locked events and user preferences
    - Adapts to manual changes
    - Includes travel time buffers
    """

    def __init__(self):
        self.agent = Agent(
            name="ScheduleMakerAgent",
            model=BedrockModel(model_id='anthropic.claude-3-5-sonnet-20240620-v1:0'),
            system_prompt="""You are an intelligent study schedule planner for college students.

Your role:
1. Create optimal study schedules based on assignments, exams, and classes
2. Respect locked events (user-set appointments)
3. Add appropriate breaks between study sessions
4. Include travel time buffers between events
5. Prioritize courses when requested by the user
6. Adapt to the student's wellness state (add more breaks if stressed)

Scheduling rules:
- Study blocks: Use user's preferred duration (default 60 min)
- Breaks: Use user's preferred duration (default 15 min)
- Travel buffers: Use user's preferred duration (default 10 min)
- Never schedule over locked events
- Schedule more intensive study sessions earlier in the day when possible
- Leave evenings lighter if student is stressed
- For prioritized courses, allocate more study blocks

When generating schedules:
- Work backwards from deadlines
- Distribute study time evenly across available days
- Don't create back-to-back study blocks without breaks
- Respect recurring blocked times (e.g., meal times, sleep)
"""
        )

    async def generate_schedule(
        self,
        assignments: List[Dict[str, Any]],
        existing_events: List[Dict[str, Any]],
        user_preferences: Dict[str, Any],
        prioritize_courses: List[str] = [],
        wellness_state: str = "normal"
    ) -> Dict[str, Any]:
        """Generate an optimized study schedule"""

        prompt = f"""
Assignments to schedule:
{json.dumps(assignments, indent=2, default=str)}

Existing events (classes, exams, locked events):
{json.dumps(existing_events, indent=2, default=str)}

User preferences:
{json.dumps(user_preferences, indent=2)}

Prioritize these courses: {prioritize_courses}
Wellness state: {wellness_state}

Generate a study schedule with:
1. Study blocks for each assignment (type: STUDY_BLOCK)
2. Break blocks between study sessions (type: BREAK)
3. Consider travel time between physical events

Return JSON array of events:
[
  {{
    "type": "STUDY_BLOCK" or "BREAK",
    "title": "Study: [Assignment Name]" or "Break",
    "course_id": "course_id",
    "assignment_id": "assignment_id",
    "start_time": "ISO datetime",
    "end_time": "ISO datetime",
    "is_locked": false
  }}
]
"""

        try:
            response = await self.agent.invoke_async(prompt)
            schedule = self._parse_schedule_response(response)
            return {
                "success": True,
                "schedule": schedule,
                "message": f"Generated {len(schedule)} schedule blocks"
            }
        except Exception as e:
            print(f"Error generating schedule: {e}")
            return {
                "success": False,
                "schedule": [],
                "message": f"Failed to generate schedule: {str(e)}"
            }

    def _parse_schedule_response(self, response) -> List[Dict[str, Any]]:
        """Parse the schedule from agent response"""
        try:
            # Extract content from response
            if hasattr(response, 'content'):
                content = response.content
            elif isinstance(response, str):
                content = response
            else:
                content = str(response)

            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return []
        except Exception as e:
            print(f"Error parsing schedule: {e}")
            return []


# Global agent instance
_schedule_maker_agent = None


def get_schedule_maker_agent() -> ScheduleMakerAgent:
    """Get the schedule maker agent instance (singleton)"""
    global _schedule_maker_agent
    if _schedule_maker_agent is None:
        _schedule_maker_agent = ScheduleMakerAgent()
    return _schedule_maker_agent
