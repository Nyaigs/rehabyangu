import React from 'react';
import { Link, useLocation } from '@tanstack/react-router';
import {
  HomeIcon,
  UsersIcon,
  UserPlusIcon,
  ClipboardDocumentListIcon,
  HeartIcon,
  BeakerIcon,
  CalendarDaysIcon,
  CreditCardIcon,
  CubeIcon,
  DocumentChartBarIcon,
  UserGroupIcon,
  Cog6ToothIcon,
  QuestionMarkCircleIcon,
} from '@heroicons/react/24/outline';

interface NavItem {
  path: string;
  label: string;
  icon: React.ForwardRefExoticComponent<React.SVGProps<SVGSVGElement>>;
  group: 'overview' | 'care' | 'operations' | 'system';
}

const navItems: NavItem[] = [
  { path: '/', label: 'Dashboard', icon: HomeIcon, group: 'overview' },
  { path: '/patients', label: 'Patients', icon: UsersIcon, group: 'care' },
  { path: '/admissions', label: 'Admissions', icon: UserPlusIcon, group: 'care' },
  { path: '/clinical-notes', label: 'Clinical Notes', icon: ClipboardDocumentListIcon, group: 'care' },
  { path: '/vitals', label: 'Vitals', icon: HeartIcon, group: 'care' },
  { path: '/medication', label: 'Medication', icon: BeakerIcon, group: 'care' },
  { path: '/appointments', label: 'Appointments', icon: CalendarDaysIcon, group: 'operations' },
  { path: '/billing', label: 'Billing', icon: CreditCardIcon, group: 'operations' },
  { path: '/inventory', label: 'Inventory', icon: CubeIcon, group: 'operations' },
  { path: '/reports', label: 'Reports', icon: DocumentChartBarIcon, group: 'operations' },
  { path: '/staff', label: 'Staff', icon: UserGroupIcon, group: 'system' },
  { path: '/settings', label: 'Settings', icon: Cog6ToothIcon, group: 'system' },
  { path: '/help', label: 'Help', icon: QuestionMarkCircleIcon, group: 'system' },
];

const Sidebar: React.FC = () => {
  const location = useLocation();
  const groups = [
    { name: 'Overview', key: 'overview' },
    { name: 'Care', key: 'care' },
    { name: 'Operations', key: 'operations' },
    { name: 'System', key: 'system' },
  ];

  return (
    <aside className="w-56 bg-primary-700 text-white h-screen flex flex-col fixed left-0 top-0 z-40">
      <div className="flex items-center h-14 px-4 border-b border-primary-800">
        <span className="text-lg font-semibold tracking-tight">RehabYangu</span>
      </div>
      <nav className="flex-1 overflow-y-auto p-3 space-y-4">
        {groups.map((group) => {
          const items = navItems.filter(i => i.group === group.key);
          if (items.length === 0) return null;
          return (
            <div key={group.key}>
              <div className="text-[10px] font-semibold uppercase tracking-wider text-secondary-300 mb-1">
                {group.name}
              </div>
              <div className="space-y-0.5">
                {items.map((item) => (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-150 ${
                      location.pathname === item.path
                        ? 'bg-primary-600 text-white shadow-sm'
                        : 'text-secondary-200 hover:bg-primary-600/50 hover:text-white'
                    }`}
                  >
                    <item.icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </Link>
                ))}
              </div>
            </div>
          );
        })}
      </nav>
      <div className="p-4 border-t border-primary-800 text-[10px] text-secondary-300">
        RehabYangu v1.0
      </div>
    </aside>
  );
};

export default Sidebar;
