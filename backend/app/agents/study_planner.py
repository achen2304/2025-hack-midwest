"""
Study Planner Agent - Creates personalized study guides using RAG
"""
from typing import List, Dict, Any
from strands import Agent
import json


class StudyPlannerAgent:
    """
    AI agent that creates personalized study guides using RAG.
    - Ingests course materials (notes, slides)
    - Uses vector search to find relevant information
    - Generates comprehensive study plans for exams
    """

    def __init__(self, vector_search_service):
        self.vector_search = vector_search_service
        self.agent = Agent(
            name="StudyPlannerAgent",
            system_prompt="""You are an expert academic tutor who creates personalized study guides.

Your role:
1. Analyze course materials provided via vector search
2. Create comprehensive study guides for exams and quizzes
3. Break down complex topics into manageable sections
4. Suggest practice problems and review strategies
5. Prioritize topics based on importance and difficulty

When creating study guides:
- Start with high-level overview
- Break into specific topics and subtopics
- Include key concepts, formulas, and examples
- Suggest time allocation for each topic
- Recommend practice exercises
- Identify potentially difficult areas
"""
        )

    async def create_study_guide(
        self,
        exam_info: Dict[str, Any],
        course_materials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create a study guide for an exam"""

        prompt = f"""
Exam: {exam_info.get('title', 'Unknown')}
Course: {exam_info.get('course_name', 'Unknown')}
Date: {exam_info.get('date', 'Unknown')}

Relevant course materials:
{json.dumps(course_materials, indent=2)}

Create a comprehensive study guide with:
1. Overview of topics to cover
2. Breakdown of each topic with key concepts
3. Recommended time allocation
4. Practice suggestions
5. Areas that may need extra attention

Format as JSON:
{{
  "overview": "Brief overview",
  "topics": [
    {{
      "name": "Topic name",
      "key_concepts": ["concept1", "concept2"],
      "time_allocation_minutes": 60,
      "difficulty": "easy/medium/hard",
      "practice_suggestions": "What to practice"
    }}
  ],
  "total_study_hours": 10
}}
"""

        try:
            response = await self.agent.run_async(prompt)
            study_guide = self._parse_study_guide(response)
            return {
                "success": True,
                "study_guide": study_guide,
                "message": "Study guide created successfully"
            }
        except Exception as e:
            print(f"Error creating study guide: {e}")
            return {
                "success": False,
                "study_guide": {},
                "message": f"Failed to create study guide: {str(e)}"
            }

    def _parse_study_guide(self, response) -> Dict[str, Any]:
        """Parse study guide from response"""
        try:
            # Extract content from response
            if hasattr(response, 'content'):
                content = response.content
            elif isinstance(response, str):
                content = response
            else:
                content = str(response)

            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"raw_content": content}
        except Exception as e:
            print(f"Error parsing study guide: {e}")
            return {"raw_content": str(response)}


def create_study_planner_agent(vector_service):
    """Create study planner agent with vector search dependency"""
    return StudyPlannerAgent(vector_service)
