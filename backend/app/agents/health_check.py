"""
Health Check Agent - Monitors student wellness and adjusts check-in frequency
"""
from typing import List, Dict, Any, Optional
from strands import Agent
import json


class HealthCheckAgent:
    """
    AI agent that monitors student wellness and adjusts schedules accordingly.
    - Analyzes sentiment of user responses
    - Adapts check-in frequency based on stress levels
    - Coordinates with Schedule Maker to inject breaks when needed
    """

    def __init__(self):
        self.agent = Agent(
            name="HealthCheckAgent",
            system_prompt="""You are a compassionate wellness companion for college students.

Your role:
1. Check in on students' emotional well-being during study sessions
2. Analyze the sentiment of their responses (positive, neutral, negative, stressed)
3. Provide empathetic support and suggestions
4. Track feelings per course to identify patterns
5. Recommend when to take breaks or adjust study schedules

When analyzing student responses:
- Be empathetic and supportive
- Detect stress indicators like "overwhelmed", "anxious", "tired", "can't focus"
- Detect positive indicators like "good", "confident", "ready", "motivated"
- Consider the context of what they're studying

Response format:
- sentiment: "positive", "neutral", "negative", "stressed", "overwhelmed"
- next_checkin_minutes: Adjust based on sentiment (30-120 minutes)
  - positive/neutral: 60-120 minutes
  - negative: 45 minutes
  - stressed: 30 minutes
  - overwhelmed: Immediate break recommendation
- suggestions: Brief wellness tips or encouragement
"""
        )

    async def analyze_checkin(
        self,
        user_message: str,
        current_course: Optional[str] = None,
        recent_feelings: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Analyze a health check-in from the student"""

        context = f"Student's message: {user_message}\n"
        if current_course:
            context += f"Currently studying: {current_course}\n"
        if recent_feelings:
            context += f"Recent course feelings: {json.dumps(recent_feelings, indent=2)}\n"

        prompt = f"""{context}

Analyze this student's well-being and provide:
1. sentiment: one of [positive, neutral, negative, stressed, overwhelmed]
2. next_checkin_minutes: number between 30-120
3. suggestions: brief supportive message or wellness tip
4. needs_break: true if student should take a break NOW

Respond in JSON format."""

        try:
            response = await self.agent.run_async(prompt)
            result = self._parse_response(response)
            return result
        except Exception as e:
            print(f"Error in health check analysis: {e}")
            # Fallback response
            return {
                "sentiment": "neutral",
                "next_checkin_minutes": 60,
                "suggestions": "Keep up the good work! Remember to take breaks.",
                "needs_break": False
            }

    def _parse_response(self, response) -> Dict[str, Any]:
        """Parse the agent's JSON response"""
        try:
            # Extract content from response
            if hasattr(response, 'content'):
                content = response.content
            elif isinstance(response, str):
                content = response
            else:
                content = str(response)

            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback parsing
                return {
                    "sentiment": "neutral",
                    "next_checkin_minutes": 60,
                    "suggestions": content,
                    "needs_break": False
                }
        except Exception as e:
            print(f"Error parsing response: {e}")
            return {
                "sentiment": "neutral",
                "next_checkin_minutes": 60,
                "suggestions": str(response),
                "needs_break": False
            }


# Global agent instance
_health_check_agent = None


def get_health_check_agent() -> HealthCheckAgent:
    """Get the health check agent instance (singleton)"""
    global _health_check_agent
    if _health_check_agent is None:
        _health_check_agent = HealthCheckAgent()
    return _health_check_agent
