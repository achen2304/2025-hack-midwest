"use client";

import { useAuth, useUser, UserButton } from "@clerk/nextjs";
import { useEffect, useState } from "react";

interface Course {
  id: string;
  name: string;
  course_code: string;
}

interface Assignment {
  id: string;
  title: string;
  course_name: string;
  due_at: string;
}

export default function DashboardPage() {
  const { getToken, isLoaded, isSignedIn } = useAuth();
  const { user } = useUser();
  const [courses, setCourses] = useState<Course[]>([]);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [canvasConnected, setCanvasConnected] = useState(false);

  useEffect(() => {
    if (!isLoaded || !isSignedIn) return;

    const fetchData = async () => {
      try {
        const token = await getToken();

        // Test Canvas connection
        const testResponse = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/canvas/test`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (testResponse.ok) {
          setCanvasConnected(true);

          // Fetch courses
          const coursesResponse = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/canvas/courses`,
            {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            }
          );

          if (coursesResponse.ok) {
            const coursesData = await coursesResponse.json();
            setCourses(coursesData);
          }

          // Fetch upcoming assignments
          const assignmentsResponse = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/canvas/assignments/upcoming?days_ahead=7`,
            {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            }
          );

          if (assignmentsResponse.ok) {
            const assignmentsData = await assignmentsResponse.json();
            setAssignments(assignmentsData.data?.assignments || []);
          }
        }
      } catch (err) {
        console.error("Error fetching data:", err);
        setError("Failed to load data. Canvas may not be connected.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [isLoaded, isSignedIn, getToken]);

  if (!isLoaded || !isSignedIn) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">CampusMind</h1>
              <p className="text-sm text-gray-600">
                Welcome back, {user?.firstName || user?.emailAddresses[0]?.emailAddress}!
              </p>
            </div>
            <UserButton afterSignOutUrl="/" />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Status Card */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Connection Status</h2>
          <div className="space-y-2">
            <div className="flex items-center">
              <div
                className={`w-3 h-3 rounded-full mr-3 ${
                  canvasConnected ? "bg-green-500" : "bg-red-500"
                }`}
              ></div>
              <span className="text-sm">
                Canvas LMS: {canvasConnected ? "Connected" : "Not Connected"}
              </span>
            </div>
            {!canvasConnected && (
              <p className="text-sm text-gray-600 ml-6">
                Connect Canvas in settings to sync your courses and assignments
              </p>
            )}
          </div>
        </div>

        {error && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-yellow-800">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Courses */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6">
              <h2 className="text-lg font-semibold mb-4">Your Courses</h2>
              {loading ? (
                <p className="text-sm text-gray-500">Loading courses...</p>
              ) : courses.length > 0 ? (
                <ul className="space-y-3">
                  {courses.map((course) => (
                    <li
                      key={course.id}
                      className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition"
                    >
                      <p className="font-medium text-gray-900">{course.name}</p>
                      <p className="text-sm text-gray-500">{course.course_code}</p>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-500 mb-2">No courses found</p>
                  <p className="text-sm text-gray-400">
                    Connect your Canvas account to see your courses
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Upcoming Assignments */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6">
              <h2 className="text-lg font-semibold mb-4">Upcoming Assignments</h2>
              {loading ? (
                <p className="text-sm text-gray-500">Loading assignments...</p>
              ) : assignments.length > 0 ? (
                <ul className="space-y-3">
                  {assignments.map((assignment) => (
                    <li
                      key={assignment.id}
                      className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition"
                    >
                      <p className="font-medium text-gray-900">{assignment.title}</p>
                      <p className="text-sm text-gray-500">{assignment.course_name}</p>
                      {assignment.due_at && (
                        <p className="text-xs text-gray-400 mt-1">
                          Due: {new Date(assignment.due_at).toLocaleDateString()}
                        </p>
                      )}
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-500 mb-2">No upcoming assignments</p>
                  <p className="text-sm text-gray-400">
                    You're all caught up! 🎉
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-6 bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {!canvasConnected && (
              <a
                href="/settings"
                className="px-4 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition text-center font-medium"
              >
                Connect Canvas
              </a>
            )}
            <button className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
              Sync Canvas
            </button>
            <button className="px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition">
              View Calendar
            </button>
            <button className="px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition">
              Ask AI Agent
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
