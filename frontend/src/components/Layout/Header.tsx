import React, { useState, useRef, useEffect } from 'react';
import { Link } from '@tanstack/react-router';
import {
  MagnifyingGlassIcon,
  PlusIcon,
  UserCircleIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
} from '@heroicons/react/24/outline';
import { useAuth } from '../../context/AuthContext';
import NotificationBell from '../NotificationBell';

const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <header className="h-12 bg-white border-b border-secondary-200 px-4 flex items-center justify-between sticky top-0 z-30 shadow-sm">
      <div className="flex items-center gap-3 flex-1">
        <div className="hidden md:flex items-center gap-2 bg-secondary-50 border border-secondary-200 rounded-md px-2.5 py-1 w-64 lg:w-72 transition-all focus-within:border-primary-600 focus-within:ring-1 focus-within:ring-primary-200">
          <MagnifyingGlassIcon className="w-3.5 h-3.5 text-secondary-400" />
          <input
            type="text"
            placeholder="Search patients, appointments..."
            className="bg-transparent border-none outline-none text-sm w-full text-secondary-700 placeholder-secondary-400"
          />
          <kbd className="text-[10px] text-secondary-400 border border-secondary-200 rounded px-1">⌘K</kbd>
        </div>
      </div>

      <div className="flex items-center gap-1.5">
        <NotificationBell />
        <button className="p-1.5 rounded-md hover:bg-secondary-100 text-secondary-500 transition-colors">
          <PlusIcon className="w-3.5 h-3.5" />
        </button>
        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-1.5 p-1 rounded-full hover:bg-secondary-100 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-200"
          >
            <div className="w-7 h-7 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-xs font-semibold">
              {user?.username?.charAt(0).toUpperCase() || 'U'}
            </div>
            <span className="hidden sm:inline text-xs font-medium text-secondary-700">
              {user?.username}
            </span>
          </button>
          {showUserMenu && (
            <div className="absolute right-0 mt-2 w-44 bg-white rounded-md shadow-dropdown border border-secondary-100 overflow-hidden z-50">
              <div className="p-2.5 border-b border-secondary-100">
                <p className="text-xs font-semibold text-secondary-800">{user?.username}</p>
                <p className="text-[11px] text-secondary-500">{user?.email}</p>
              </div>
              <div className="p-1">
                <Link
                  to="/profile"
                  className="flex items-center gap-2 px-2.5 py-1.5 text-xs text-secondary-700 hover:bg-secondary-50 rounded transition-colors"
                  onClick={() => setShowUserMenu(false)}
                >
                  <UserCircleIcon className="w-3.5 h-3.5" /> Profile
                </Link>
                <Link
                  to="/settings"
                  className="flex items-center gap-2 px-2.5 py-1.5 text-xs text-secondary-700 hover:bg-secondary-50 rounded transition-colors"
                  onClick={() => setShowUserMenu(false)}
                >
                  <Cog6ToothIcon className="w-3.5 h-3.5" /> Settings
                </Link>
                <button
                  onClick={() => { setShowUserMenu(false); logout(); }}
                  className="flex items-center gap-2 px-2.5 py-1.5 text-xs text-danger hover:bg-danger-light rounded w-full transition-colors"
                >
                  <ArrowRightOnRectangleIcon className="w-3.5 h-3.5" /> Logout
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
