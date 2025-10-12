'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { redirect } from 'next/navigation'

export default function TestPage() {
  const { data: session, status } = useSession()

  // User Profile State
  const [profile, setProfile] = useState<any>(null)
  const [name, setName] = useState('')
  const [university, setUniversity] = useState('')

  // Canvas State
  const [canvasToken, setCanvasToken] = useState('')
  const [canvasBaseUrl, setCanvasBaseUrl] = useState('https://canvas.instructure.com')
  const [hasToken, setHasToken] = useState(false)
  const [courses, setCourses] = useState<any[]>([])
  const [assignments, setAssignments] = useState<any[]>([])
  const [selectedCourseIds, setSelectedCourseIds] = useState<string[]>([])

  // Preferences State
  const [studyBlockDuration, setStudyBlockDuration] = useState(60)
  const [breakDuration, setBreakDuration] = useState(15)
  const [travelDuration, setTravelDuration] = useState(10)

  // Response Messages
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  // Redirect if not authenticated
  if (status === 'unauthenticated') {
    redirect('/login')
  }

  // Fetch user profile on load
  useEffect(() => {
    if (status === 'authenticated') {
      fetchProfile()
      checkCanvasToken()
    }
  }, [status])

  const fetchProfile = async () => {
    try {
      const res = await fetch('/api/backend/user/profile')
      if (res.ok) {
        const data = await res.json()
        setProfile(data)
        setName(data.name || '')
        setUniversity(data.university || '')
      } else {
        setError('Failed to fetch profile')
      }
    } catch (err) {
      setError('Error fetching profile: ' + err)
    }
  }

  const updateProfile = async () => {
    try {
      const res = await fetch('/api/backend/user/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, university })
      })

      if (res.ok) {
        const data = await res.json()
        setProfile(data)
        setMessage('Profile updated successfully!')
        setTimeout(() => setMessage(''), 3000)
      } else {
        setError('Failed to update profile')
      }
    } catch (err) {
      setError('Error updating profile: ' + err)
    }
  }

  const checkCanvasToken = async () => {
    try {
      const res = await fetch('/api/backend/canvas/token/status')
      if (res.ok) {
        const data = await res.json()
        setHasToken(data.has_token)
      }
    } catch (err) {
      console.error('Error checking Canvas token:', err)
    }
  }

  const saveCanvasToken = async () => {
    try {
      const res = await fetch('/api/backend/canvas/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          canvas_token: canvasToken,
          canvas_base_url: canvasBaseUrl
        })
      })

      if (res.ok) {
        setMessage('Canvas token saved successfully!')
        setHasToken(true)
        setCanvasToken('')
        setTimeout(() => setMessage(''), 3000)
      } else {
        const data = await res.json()
        setError('Failed to save Canvas token: ' + data.detail)
      }
    } catch (err) {
      setError('Error saving Canvas token: ' + err)
    }
  }

  const deleteCanvasToken = async () => {
    try {
      const res = await fetch('/api/backend/canvas/token', {
        method: 'DELETE'
      })

      if (res.ok) {
        setMessage('Canvas token removed successfully!')
        setHasToken(false)
        setCourses([])
        setAssignments([])
        setTimeout(() => setMessage(''), 3000)
      } else {
        setError('Failed to delete Canvas token')
      }
    } catch (err) {
      setError('Error deleting Canvas token: ' + err)
    }
  }

  const fetchCourses = async () => {
    try {
      const res = await fetch('/api/backend/canvas/courses')
      if (res.ok) {
        const data = await res.json()
        setCourses(data)
        // Pre-select already tracked courses
        const trackedIds = data.filter((c: any) => c.is_tracked).map((c: any) => c.id)
        setSelectedCourseIds(trackedIds)
        setMessage(`Fetched ${data.length} courses!`)
        setTimeout(() => setMessage(''), 3000)
      } else {
        const data = await res.json()
        setError('Failed to fetch courses: ' + data.detail)
      }
    } catch (err) {
      setError('Error fetching courses: ' + err)
    }
  }

  const toggleCourseSelection = (courseId: string) => {
    setSelectedCourseIds(prev => {
      if (prev.includes(courseId)) {
        return prev.filter(id => id !== courseId)
      } else {
        return [...prev, courseId]
      }
    })
  }

  const saveTrackedCourses = async () => {
    try {
      const res = await fetch('/api/backend/canvas/courses/track', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ course_ids: selectedCourseIds })
      })

      if (res.ok) {
        const data = await res.json()
        setMessage(data.message)
        // Refresh courses to update is_tracked status
        await fetchCourses()
        setTimeout(() => setMessage(''), 3000)
      } else {
        const data = await res.json()
        setError('Failed to save tracked courses: ' + data.detail)
      }
    } catch (err) {
      setError('Error saving tracked courses: ' + err)
    }
  }

  const fetchAssignments = async () => {
    try {
      const res = await fetch('/api/backend/canvas/assignments')
      if (res.ok) {
        const data = await res.json()
        setAssignments(data)
        setMessage(`Fetched ${data.length} assignments!`)
        setTimeout(() => setMessage(''), 3000)
      } else {
        const data = await res.json()
        setError('Failed to fetch assignments: ' + data.detail)
      }
    } catch (err) {
      setError('Error fetching assignments: ' + err)
    }
  }

  const syncCanvasData = async () => {
    try {
      const res = await fetch('/api/backend/canvas/sync', {
        method: 'POST'
      })

      if (res.ok) {
        const data = await res.json()
        setMessage(data.message)
        setTimeout(() => setMessage(''), 3000)
      } else {
        const data = await res.json()
        setError('Failed to sync Canvas data: ' + data.detail)
      }
    } catch (err) {
      setError('Error syncing Canvas data: ' + err)
    }
  }

  const updatePreferences = async () => {
    try {
      const res = await fetch('/api/backend/user/preferences', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          study_block_duration: studyBlockDuration,
          break_duration: breakDuration,
          travel_duration: travelDuration,
          recurring_blocked_times: []
        })
      })

      if (res.ok) {
        setMessage('Preferences updated successfully!')
        setTimeout(() => setMessage(''), 3000)
      } else {
        setError('Failed to update preferences')
      }
    } catch (err) {
      setError('Error updating preferences: ' + err)
    }
  }

  if (status === 'loading') {
    return <div className="p-8">Loading...</div>
  }

  return (
    <div className="max-w-4xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">API Test Page</h1>

      {/* Messages */}
      {message && (
        <div className="mb-4 p-4 bg-green-100 text-green-800 rounded-lg">
          {message}
        </div>
      )}
      {error && (
        <div className="mb-4 p-4 bg-red-100 text-red-800 rounded-lg">
          {error}
          <button onClick={() => setError('')} className="ml-4 underline">Dismiss</button>
        </div>
      )}

      {/* Session Info */}
      <div className="mb-8 p-6 bg-gray-100 rounded-lg">
        <h2 className="text-xl font-semibold mb-4">Session Info</h2>
        <p><strong>Email:</strong> {session?.user?.email}</p>
        <p><strong>Name:</strong> {session?.user?.name}</p>
      </div>

      {/* User Profile Section */}
      <div className="mb-8 p-6 border rounded-lg">
        <h2 className="text-xl font-semibold mb-4">User Profile</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full p-2 border rounded"
              placeholder="Enter your name"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">University</label>
            <input
              type="text"
              value={university}
              onChange={(e) => setUniversity(e.target.value)}
              className="w-full p-2 border rounded"
              placeholder="Enter your university"
            />
          </div>

          <button
            onClick={updateProfile}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Update Profile
          </button>
        </div>

        {profile && (
          <div className="mt-4 p-4 bg-gray-50 rounded">
            <h3 className="font-semibold mb-2">Current Profile:</h3>
            <pre className="text-sm">{JSON.stringify(profile, null, 2)}</pre>
          </div>
        )}
      </div>

      {/* User Preferences Section */}
      <div className="mb-8 p-6 border rounded-lg">
        <h2 className="text-xl font-semibold mb-4">User Preferences</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Study Block Duration (minutes)</label>
            <input
              type="number"
              value={studyBlockDuration}
              onChange={(e) => setStudyBlockDuration(parseInt(e.target.value))}
              className="w-full p-2 border rounded"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Break Duration (minutes)</label>
            <input
              type="number"
              value={breakDuration}
              onChange={(e) => setBreakDuration(parseInt(e.target.value))}
              className="w-full p-2 border rounded"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Travel Duration (minutes)</label>
            <input
              type="number"
              value={travelDuration}
              onChange={(e) => setTravelDuration(parseInt(e.target.value))}
              className="w-full p-2 border rounded"
            />
          </div>

          <button
            onClick={updatePreferences}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Update Preferences
          </button>
        </div>
      </div>

      {/* Canvas Integration Section */}
      <div className="mb-8 p-6 border rounded-lg">
        <h2 className="text-xl font-semibold mb-4">Canvas Integration</h2>

        <p className="mb-4">
          <strong>Status:</strong> {hasToken ? '✓ Token Configured' : '✗ No Token'}
        </p>

        {!hasToken ? (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Canvas Personal Access Token</label>
              <input
                type="password"
                value={canvasToken}
                onChange={(e) => setCanvasToken(e.target.value)}
                className="w-full p-2 border rounded"
                placeholder="Enter your Canvas token"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Canvas Base URL</label>
              <input
                type="text"
                value={canvasBaseUrl}
                onChange={(e) => setCanvasBaseUrl(e.target.value)}
                className="w-full p-2 border rounded"
                placeholder="https://canvas.instructure.com"
              />
            </div>

            <button
              onClick={saveCanvasToken}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Save Canvas Token
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex space-x-2">
              <button
                onClick={fetchCourses}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Fetch Courses
              </button>

              <button
                onClick={fetchAssignments}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Fetch Assignments
              </button>

              <button
                onClick={syncCanvasData}
                className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
              >
                Sync to Database
              </button>

              <button
                onClick={deleteCanvasToken}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
              >
                Remove Token
              </button>
            </div>

            {courses.length > 0 && (
              <div className="mt-4 p-4 bg-gray-50 rounded">
                <div className="flex justify-between items-center mb-2">
                  <h3 className="font-semibold">Courses ({courses.length}):</h3>
                  <button
                    onClick={saveTrackedCourses}
                    className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
                    disabled={selectedCourseIds.length === 0}
                  >
                    Save Selected ({selectedCourseIds.length})
                  </button>
                </div>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {courses.map((course) => (
                    <div
                      key={course.id}
                      className={`p-2 bg-white rounded border flex items-start space-x-2 cursor-pointer hover:bg-gray-50 ${
                        selectedCourseIds.includes(course.id) ? 'border-blue-500 bg-blue-50' : ''
                      }`}
                      onClick={() => toggleCourseSelection(course.id)}
                    >
                      <input
                        type="checkbox"
                        checked={selectedCourseIds.includes(course.id)}
                        onChange={() => toggleCourseSelection(course.id)}
                        className="mt-1 cursor-pointer"
                        onClick={(e) => e.stopPropagation()}
                      />
                      <div className="flex-1">
                        <p className="font-medium">{course.name}</p>
                        <p className="text-sm text-gray-600">{course.course_code}</p>
                        {course.is_tracked && (
                          <span className="inline-block mt-1 px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded">
                            Tracked
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {assignments.length > 0 && (
              <div className="mt-4 p-4 bg-gray-50 rounded">
                <h3 className="font-semibold mb-2">Assignments ({assignments.length}):</h3>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {assignments.map((assignment) => (
                    <div key={assignment.id} className="p-2 bg-white rounded border">
                      <p className="font-medium">{assignment.name}</p>
                      <p className="text-sm text-gray-600">
                        Due: {assignment.due_at ? new Date(assignment.due_at).toLocaleString() : 'No due date'}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
