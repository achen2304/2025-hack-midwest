'use client'

import { useState } from 'react'
import { Brain, Heart, BookOpen, Users, Calendar, Target } from 'lucide-react'
import { useSession } from 'next-auth/react'
import { redirect } from 'next/navigation'

export default function Home() {
  const [selectedTab, setSelectedTab] = useState('today')

  const tabs = [
    { id: 'today', label: 'Today', icon: Calendar },
    { id: 'study', label: 'Study', icon: BookOpen },
    { id: 'wellness', label: 'Wellness', icon: Heart },
    { id: 'connect', label: 'Connect', icon: Users },
  ]

  const renderContent = () => {
    switch (selectedTab) {
      case 'today':
        return (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-primary-600 to-secondary-600 text-white p-8 rounded-xl">
              <h2 className="text-2xl font-bold mb-2">Good morning, Student!</h2>
              <p className="text-primary-100">Here's your personalized overview for today.</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="card">
                <div className="flex items-center mb-4">
                  <Target className="h-6 w-6 text-primary-600 mr-2" />
                  <h3 className="text-lg font-semibold">Today's Goals</h3>
                </div>
                <p className="text-gray-600">Complete calculus homework</p>
                <p className="text-gray-600">Review biology notes</p>
                <p className="text-gray-600">Journal entry</p>
              </div>
              
              <div className="card">
                <div className="flex items-center mb-4">
                  <Calendar className="h-6 w-6 text-secondary-600 mr-2" />
                  <h3 className="text-lg font-semibold">Upcoming</h3>
                </div>
                <p className="text-gray-600">Physics exam - Tomorrow</p>
                <p className="text-gray-600">Group project - Friday</p>
              </div>
              
              <div className="card">
                <div className="flex items-center mb-4">
                  <Brain className="h-6 w-6 text-accent-600 mr-2" />
                  <h3 className="text-lg font-semibold">AI Insights</h3>
                </div>
                <p className="text-gray-600">Your study patterns are improving!</p>
                <p className="text-gray-600">Consider taking breaks every 45 minutes.</p>
              </div>
            </div>
          </div>
        )
      
      case 'study':
        return (
          <div className="space-y-6">
            <div className="card">
              <h2 className="text-2xl font-bold mb-4">Study Hub</h2>
              <p className="text-gray-600 mb-6">AI-powered study planning and academic support</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-3">Create Study Plan</h3>
                  <p className="text-gray-600 mb-4">Get personalized study plans based on your courses and preferences.</p>
                  <button className="btn-primary">Create Plan</button>
                </div>
                
                <div className="border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-3">Assignment Tracker</h3>
                  <p className="text-gray-600 mb-4">Track and manage your assignments with AI assistance.</p>
                  <button className="btn-secondary">View Assignments</button>
                </div>
              </div>
            </div>
          </div>
        )
      
      case 'wellness':
        return (
          <div className="space-y-6">
            <div className="card">
              <h2 className="text-2xl font-bold mb-4">Wellness Center</h2>
              <p className="text-gray-600 mb-6">Mental health support and wellness tracking</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-3">Mood Tracker</h3>
                  <p className="text-gray-600 mb-4">Track your mood and get insights into your emotional patterns.</p>
                  <button className="btn-primary">Track Mood</button>
                </div>
                
                <div className="border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-3">Journal</h3>
                  <p className="text-gray-600 mb-4">Express your thoughts and feelings in a safe space.</p>
                  <button className="btn-secondary">Write Entry</button>
                </div>
              </div>
            </div>
          </div>
        )
      
      case 'connect':
        return (
          <div className="space-y-6">
            <div className="card">
              <h2 className="text-2xl font-bold mb-4">Connect</h2>
              <p className="text-gray-600 mb-6">Connect with your academic community</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-3">Study Groups</h3>
                  <p className="text-gray-600 mb-4">Find and join study groups for your courses.</p>
                  <button className="btn-primary">Find Groups</button>
                </div>
                
                <div className="border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-3">Peer Support</h3>
                  <p className="text-gray-600 mb-4">Connect with peers for mutual support and motivation.</p>
                  <button className="btn-secondary">Connect</button>
                </div>
              </div>
            </div>
          </div>
        )
      
      default:
        return null
    }
  }

  const { data: session, status } = useSession()

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">CampusMind</h1>
        <p className="text-xl text-gray-600">Your AI-powered academic and wellness companion</p>
      </div>
      
      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-8">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setSelectedTab(tab.id)}
                className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                  selectedTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-5 w-5 mr-2" />
                {tab.label}
              </button>
            )
          })}
        </nav>
      </div>
      
      {/* Tab Content */}
      {renderContent()}
    </div>
  )
}
