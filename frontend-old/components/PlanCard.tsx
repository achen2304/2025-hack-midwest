'use client'

import { useState } from 'react'
import { Calendar, Clock, CheckCircle, Circle, MoreVertical } from 'lucide-react'

interface PlanCardProps {
  title: string
  description?: string
  dueDate?: string
  completed?: boolean
  tasks?: Array<{
    id: string
    title: string
    completed: boolean
  }>
  onToggleComplete?: (planId: string) => void
  onEdit?: (planId: string) => void
  onDelete?: (planId: string) => void
}

export default function PlanCard({
  title,
  description,
  dueDate,
  completed = false,
  tasks = [],
  onToggleComplete,
  onEdit,
  onDelete
}: PlanCardProps) {
  const [showTasks, setShowTasks] = useState(false)
  const [showMenu, setShowMenu] = useState(false)

  const completedTasks = tasks.filter(task => task.completed).length
  const totalTasks = tasks.length
  const progressPercentage = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0

  return (
    <div className="card hover:shadow-xl transition-shadow duration-200">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <button
            onClick={() => onToggleComplete?.(title)}
            className="flex-shrink-0"
          >
            {completed ? (
              <CheckCircle className="h-6 w-6 text-green-500" />
            ) : (
              <Circle className="h-6 w-6 text-gray-400 hover:text-primary-500" />
            )}
          </button>
          <div>
            <h3 className={`text-lg font-semibold ${completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
              {title}
            </h3>
            {description && (
              <p className="text-gray-600 text-sm mt-1">{description}</p>
            )}
          </div>
        </div>
        
        <div className="relative">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="p-1 hover:bg-gray-100 rounded-full"
          >
            <MoreVertical className="h-5 w-5 text-gray-400" />
          </button>
          
          {showMenu && (
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-200">
              <button
                onClick={() => {
                  onEdit?.(title)
                  setShowMenu(false)
                }}
                className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                Edit Plan
              </button>
              <button
                onClick={() => {
                  onDelete?.(title)
                  setShowMenu(false)
                }}
                className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100"
              >
                Delete Plan
              </button>
            </div>
          )}
        </div>
      </div>
      
      {dueDate && (
        <div className="flex items-center text-gray-600 text-sm mb-3">
          <Calendar className="h-4 w-4 mr-1" />
          Due: {new Date(dueDate).toLocaleDateString()}
        </div>
      )}
      
      {totalTasks > 0 && (
        <div className="mb-4">
          <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
            <span>Progress</span>
            <span>{completedTasks}/{totalTasks} tasks</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </div>
      )}
      
      {totalTasks > 0 && (
        <button
          onClick={() => setShowTasks(!showTasks)}
          className="text-primary-600 hover:text-primary-700 text-sm font-medium mb-2"
        >
          {showTasks ? 'Hide' : 'Show'} Tasks ({totalTasks})
        </button>
      )}
      
      {showTasks && totalTasks > 0 && (
        <div className="space-y-2 mt-3 pt-3 border-t border-gray-200">
          {tasks.map((task) => (
            <div key={task.id} className="flex items-center space-x-2">
              {task.completed ? (
                <CheckCircle className="h-4 w-4 text-green-500" />
              ) : (
                <Circle className="h-4 w-4 text-gray-400" />
              )}
              <span className={`text-sm ${task.completed ? 'line-through text-gray-500' : 'text-gray-700'}`}>
                {task.title}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
