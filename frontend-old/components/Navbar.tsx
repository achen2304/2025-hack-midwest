'use client'

import { useState } from 'react'
import { Brain, Menu, X, Settings, LogOut, User } from 'lucide-react'
import { useRouter } from 'next/navigation'

export default function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isProfileOpen, setIsProfileOpen] = useState(false)
  const router = useRouter()

  return (
    <nav className="bg-white shadow-lg border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Brain className="h-8 w-8 text-primary-600 mr-2" />
            <span className="text-xl font-bold text-gray-900">CampusMind</span>
          </div>
          
          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <a href="#" className="text-gray-700 hover:text-primary-600 font-medium">
              Dashboard
            </a>
            <a href="#" className="text-gray-700 hover:text-primary-600 font-medium">
              Study Plans
            </a>
            <a href="#" className="text-gray-700 hover:text-primary-600 font-medium">
              Wellness
            </a>
            <a href="#" className="text-gray-700 hover:text-primary-600 font-medium">
              Canvas
            </a>
          </div>
          
          {/* Profile Dropdown */}
          <div className="hidden md:flex items-center space-x-4">
            <div className="relative">
              <button
                onClick={() => setIsProfileOpen(!isProfileOpen)}
                className="flex items-center space-x-2 text-gray-700 hover:text-primary-600"
              >
                <User className="h-6 w-6" />
                <span>Student User</span>
              </button>
            <button
              onClick={() => router.push('/login')}
              className="ml-4 px-3 py-1 bg-primary-600 text-white rounded-md hover:bg-primary-700"
            >
              Sign In
            </button>
              
              {isProfileOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50">
                  <a
                    href="#"
                    className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <Settings className="h-4 w-4 mr-2" />
                    Settings
                  </a>
                  <a
                    href="#"
                    className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <LogOut className="h-4 w-4 mr-2" />
                    Sign Out
                  </a>
                </div>
              )}
            </div>
          </div>
          
          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-gray-700 hover:text-primary-600"
            >
              {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
        
        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-gray-50 rounded-lg mt-2">
              <a
                href="#"
                className="block px-3 py-2 text-gray-700 hover:text-primary-600 font-medium"
              >
                Dashboard
              </a>
              <a
                href="#"
                className="block px-3 py-2 text-gray-700 hover:text-primary-600 font-medium"
              >
                Study Plans
              </a>
              <a
                href="#"
                className="block px-3 py-2 text-gray-700 hover:text-primary-600 font-medium"
              >
                Wellness
              </a>
              <a
                href="#"
                className="block px-3 py-2 text-gray-700 hover:text-primary-600 font-medium"
              >
                Canvas
              </a>
              <div className="border-t border-gray-200 pt-2 mt-2">
                <a
                  href="#"
                  className="flex items-center px-3 py-2 text-gray-700 hover:text-primary-600 font-medium"
                >
                  <Settings className="h-4 w-4 mr-2" />
                  Settings
                </a>
                <a
                  href="#"
                  className="flex items-center px-3 py-2 text-gray-700 hover:text-primary-600 font-medium"
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  Sign Out
                </a>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
