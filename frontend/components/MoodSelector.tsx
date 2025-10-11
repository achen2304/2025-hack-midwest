'use client'

import { useState } from 'react'
import { Smile, Frown, Meh, Heart, Zap } from 'lucide-react'

interface MoodSelectorProps {
  selectedMood?: string
  onMoodSelect: (mood: string) => void
  className?: string
}

const moodOptions = [
  {
    id: 'excellent',
    label: 'Excellent',
    icon: Zap,
    color: 'text-yellow-500',
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200'
  },
  {
    id: 'good',
    label: 'Good',
    icon: Smile,
    color: 'text-green-500',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200'
  },
  {
    id: 'okay',
    label: 'Okay',
    icon: Meh,
    color: 'text-blue-500',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200'
  },
  {
    id: 'poor',
    label: 'Poor',
    icon: Frown,
    color: 'text-orange-500',
    bgColor: 'bg-orange-50',
    borderColor: 'border-orange-200'
  },
  {
    id: 'terrible',
    label: 'Terrible',
    icon: Heart,
    color: 'text-red-500',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200'
  }
]

export default function MoodSelector({
  selectedMood,
  onMoodSelect,
  className = ''
}: MoodSelectorProps) {
  return (
    <div className={`space-y-4 ${className}`}>
      <h3 className="text-lg font-semibold text-gray-900">How are you feeling?</h3>
      
      <div className="grid grid-cols-5 gap-3">
        {moodOptions.map((mood) => {
          const Icon = mood.icon
          const isSelected = selectedMood === mood.id
          
          return (
            <button
              key={mood.id}
              onClick={() => onMoodSelect(mood.id)}
              className={`
                flex flex-col items-center p-4 rounded-lg border-2 transition-all duration-200
                ${isSelected 
                  ? `${mood.bgColor} ${mood.borderColor} ${mood.color}` 
                  : 'bg-white border-gray-200 text-gray-400 hover:border-gray-300'
                }
              `}
            >
              <Icon className="h-8 w-8 mb-2" />
              <span className="text-xs font-medium">{mood.label}</span>
            </button>
          )
        })}
      </div>
      
      {selectedMood && (
        <div className="text-center">
          <p className="text-sm text-gray-600">
            Selected: <span className="font-medium capitalize">{selectedMood}</span>
          </p>
        </div>
      )}
    </div>
  )
}
