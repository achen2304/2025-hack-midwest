#!/usr/bin/env python3
"""
Canvas API Integration Example

This script demonstrates how to use the Canvas API service
to interact with Canvas LMS programmatically.

Prerequisites:
1. Canvas Personal Access Token (generate from Canvas Account > Settings > Approved Integrations)
2. Canvas instance URL (e.g., https://your-school.instructure.com)

Usage:
    python canvas_api_example.py
"""

import os
import sys
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.canvas_service import CanvasService

def main():
    """Example usage of Canvas API service"""
    
    # Configuration - Replace with your actual values
    CANVAS_URL = "https://canvas.instructure.com"  # Replace with your Canvas URL
    CANVAS_TOKEN = "your_canvas_token_here"  # Replace with your Canvas token
    
    print("🎓 Canvas API Integration Example")
    print("=" * 50)
    
    try:
        # Initialize Canvas service
        print(f"Connecting to Canvas at: {CANVAS_URL}")
        canvas_service = CanvasService(CANVAS_URL, CANVAS_TOKEN)
        
        # Test connection
        print("\n1. Testing connection...")
        result = canvas_service.test_connection()
        if result["success"]:
            print(f"✅ Connected successfully!")
            print(f"   User: {result['user']['name']} ({result['user']['email']})")
            print(f"   Canvas URL: {result['canvas_url']}")
        else:
            print(f"❌ Connection failed: {result['error']}")
            return
        
        # Get user information
        print("\n2. Getting user information...")
        user_info = canvas_service.get_user_info()
        print(f"   User ID: {user_info['id']}")
        print(f"   Name: {user_info['name']}")
        print(f"   Email: {user_info['email']}")
        print(f"   Time Zone: {user_info.get('time_zone', 'Not set')}")
        
        # Get courses
        print("\n3. Getting courses...")
        courses = canvas_service.get_courses(enrollment_state="active", per_page=10)
        print(f"   Found {len(courses)} active courses:")
        
        for i, course in enumerate(courses[:5], 1):  # Show first 5 courses
            print(f"   {i}. {course['name']} ({course['course_code']})")
            print(f"      ID: {course['id']}, Term: {course['enrollment_term_id']}")
            if course['start_at']:
                print(f"      Start: {course['start_at']}")
        
        if len(courses) > 5:
            print(f"   ... and {len(courses) - 5} more courses")
        
        # Get assignments for first course
        if courses:
            print(f"\n4. Getting assignments for '{courses[0]['name']}'...")
            try:
                assignments = canvas_service.get_course_assignments(courses[0]['id'], per_page=10)
                print(f"   Found {len(assignments)} assignments:")
                
                for i, assignment in enumerate(assignments[:5], 1):  # Show first 5 assignments
                    print(f"   {i}. {assignment['name']}")
                    print(f"      Due: {assignment['due_at'] or 'No due date'}")
                    print(f"      Points: {assignment['points_possible'] or 'N/A'}")
                    print(f"      Status: {assignment['submission']['workflow_state']}")
                    
                if len(assignments) > 5:
                    print(f"   ... and {len(assignments) - 5} more assignments")
                    
            except ValueError as e:
                print(f"   ⚠️  Could not access assignments: {str(e)}")
        
        # Get calendar events
        print("\n5. Getting calendar events...")
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)  # Next 30 days
        
        # Get context codes for first few courses
        context_codes = []
        for course in courses[:3]:  # First 3 courses
            context_codes.append(f"course_{course['id']}")
        context_codes.append("user_self")  # Personal calendar
        
        try:
            events = canvas_service.get_calendar_events(
                context_codes=context_codes,
                start_date=start_date,
                end_date=end_date,
                per_page=10
            )
            print(f"   Found {len(events)} calendar events:")
            
            for i, event in enumerate(events[:5], 1):  # Show first 5 events
                print(f"   {i}. {event['title']}")
                print(f"      Type: {event['type']}")
                print(f"      Start: {event['start_at']}")
                print(f"      Context: {event['context_code']}")
                
            if len(events) > 5:
                print(f"   ... and {len(events) - 5} more events")
                
        except Exception as e:
            print(f"   ⚠️  Could not access calendar events: {str(e)}")
        
        print("\n✅ Example completed successfully!")
        print("\nNext steps:")
        print("1. Replace CANVAS_URL and CANVAS_TOKEN with your actual values")
        print("2. Run the CampusMind backend server")
        print("3. Use the Canvas endpoints in your frontend application")
        
    except ValueError as e:
        print(f"❌ Configuration error: {str(e)}")
        print("\nPlease check:")
        print("1. Canvas URL is correct")
        print("2. Canvas token is valid")
        print("3. Token has necessary permissions")
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()
