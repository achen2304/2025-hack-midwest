'use client';

import { SignInButton, SignUpButton, useAuth } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function HomePage() {
  const { isSignedIn, isLoaded } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isLoaded && isSignedIn) {
      router.push('/dashboard');
    }
  }, [isLoaded, isSignedIn, router]);

  if (!isLoaded) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Loading Clerk authentication...</p>
          <p className="text-sm text-gray-500">
            If this takes too long, check your Clerk configuration
          </p>
          <div className="mt-4">
            <button
              onClick={() => (window.location.href = '/dashboard')}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Skip to Dashboard (Debug)
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          {/* Hero */}
          <div className="mb-12">
            <h1 className="text-5xl font-bold text-gray-900 mb-4">
              CampusMind 🧠
            </h1>
            <p className="text-xl text-gray-700 mb-2">
              AI-powered academic and wellness assistant
            </p>
            <p className="text-lg text-gray-600">for college students</p>
          </div>

          {/* Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-4xl mb-3">📚</div>
              <h3 className="font-semibold text-lg mb-2">Canvas Integration</h3>
              <p className="text-gray-600 text-sm">
                Automatic assignment sync and deadline tracking
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-4xl mb-3">📅</div>
              <h3 className="font-semibold text-lg mb-2">Smart Scheduling</h3>
              <p className="text-gray-600 text-sm">
                AI-powered study session planning
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-4xl mb-3">🤖</div>
              <h3 className="font-semibold text-lg mb-2">AI Agents</h3>
              <p className="text-gray-600 text-sm">
                Intelligent academic and wellness support
              </p>
            </div>
          </div>

          {/* CTA */}
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold mb-4">Get Started</h2>
            <p className="text-gray-600 mb-6">
              Sign in to access your personalized academic dashboard
            </p>
            <div className="flex gap-4 justify-center">
              <SignInButton mode="modal">
                <button className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition">
                  Sign In
                </button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className="px-6 py-3 bg-gray-600 text-white rounded-lg font-medium hover:bg-gray-700 transition">
                  Sign Up
                </button>
              </SignUpButton>
            </div>
          </div>

          {/* Features List */}
          <div className="mt-12 text-left bg-white rounded-lg shadow-md p-8">
            <h3 className="text-xl font-bold mb-4">Features</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span className="text-sm">Canvas LMS Integration</span>
              </div>
              <div className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span className="text-sm">Google Calendar Sync</span>
              </div>
              <div className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span className="text-sm">AI Study Planning</span>
              </div>
              <div className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span className="text-sm">Workload Analysis</span>
              </div>
              <div className="flex items-start">
                <span className="text-yellow-500 mr-2">⏳</span>
                <span className="text-sm text-gray-500">
                  Mood Tracking (Coming Soon)
                </span>
              </div>
              <div className="flex items-start">
                <span className="text-yellow-500 mr-2">⏳</span>
                <span className="text-sm text-gray-500">
                  Wellness Journal (Coming Soon)
                </span>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="mt-8 text-sm text-gray-600">
            Built with ❤️ for Hack Midwest 2025
          </div>
        </div>
      </div>
    </div>
  );
}
