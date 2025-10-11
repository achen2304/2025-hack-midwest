'use client';

import { useAuth, UserButton } from '@clerk/nextjs';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function SettingsPage() {
  const { getToken } = useAuth();
  const router = useRouter();
  const [canvasToken, setCanvasToken] = useState('');
  const [canvasUrl, setCanvasUrl] = useState('https://canvas.iastate.edu');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleConnectCanvas = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const token = await getToken();

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/canvas/connect`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            canvas_token: canvasToken,
            canvas_base_url: canvasUrl,
          }),
        }
      );

      const data = await response.json();

      if (response.ok) {
        setMessage(
          `✅ Canvas connected successfully! Welcome ${data.data?.user}`
        );
        setTimeout(() => router.push('/dashboard'), 2000);
      } else {
        setMessage(`❌ Error: ${data.detail || 'Failed to connect Canvas'}`);
      }
    } catch (err) {
      setMessage(
        '❌ Error connecting to Canvas. Check your token and try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
            <UserButton afterSignOutUrl="/" />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-6">Connect Canvas LMS</h2>

          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h3 className="font-medium text-blue-900 mb-2">
              How to get your Canvas token:
            </h3>
            <ol className="list-decimal list-inside text-sm text-blue-800 space-y-1">
              <li>Go to Canvas → Settings</li>
              <li>Scroll to "Approved Integrations"</li>
              <li>Click "+ New Access Token"</li>
              <li>Give it a purpose (e.g., "CampusMind")</li>
              <li>Copy the token and paste below</li>
            </ol>
          </div>

          <form onSubmit={handleConnectCanvas} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Canvas Base URL
              </label>
              <input
                type="url"
                value={canvasUrl}
                onChange={(e) => setCanvasUrl(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="https://canvas.iastate.edu"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Canvas Personal Access Token
              </label>
              <input
                type="password"
                value={canvasToken}
                onChange={(e) => setCanvasToken(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="10835~xxxxxxxxxxxxx"
                required
              />
              <p className="mt-1 text-xs text-gray-500">
                Your token is stored securely and never shared
              </p>
            </div>

            {message && (
              <div
                className={`p-4 rounded-lg ${
                  message.includes('✅')
                    ? 'bg-green-50 text-green-800 border border-green-200'
                    : 'bg-red-50 text-red-800 border border-red-200'
                }`}
              >
                {message}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Connecting...' : 'Connect Canvas'}
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-gray-200">
            <button
              onClick={() => router.push('/dashboard')}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              ← Back to Dashboard
            </button>
          </div>
        </div>

        {/* Quick Start Guide */}
        <div className="mt-6 bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold mb-4">Already have a token?</h3>
          <p className="text-sm text-gray-600 mb-4">
            For ISU students, your Canvas token is:{' '}
            <code className="bg-gray-100 px-2 py-1 rounded">10835~2aJ...</code>
          </p>
          <button
            onClick={() => {
              setCanvasToken(
                '10835~2aJcuerDyLmawuJWKGXmWMzwM6kXPkaP7B2Lv4xT9QRFeM2EnvwVruQfTYtvKUKX'
              );
              setMessage(
                "💡 Token pre-filled! Click 'Connect Canvas' to proceed."
              );
            }}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            Use ISU Demo Token
          </button>
        </div>
      </main>
    </div>
  );
}
