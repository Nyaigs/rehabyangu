import { useState, type ComponentType, type SVGProps } from 'react';
import { Link, useLocation } from '@tanstack/react-router';
import { Bars3Icon, CalendarDaysIcon, ChartBarIcon, ChevronLeftIcon, ChevronRightIcon, ClipboardDocumentListIcon, Cog6ToothIcon, CreditCardIcon, CubeIcon, HeartIcon, HomeIcon, QuestionMarkCircleIcon, UserGroupIcon, UserPlusIcon, UsersIcon, XMarkIcon, BuildingOffice2Icon } from '@heroicons/react/24/outline';
import { useAuth } from '../../context/AuthContext';
import { resolveMediaUrl } from '../../api/client';

type Icon = ComponentType<SVGProps<SVGSVGElement>>;
type NavItem = { path: string; label: string; icon: Icon; group: 'overview' | 'care' | 'operations' | 'administration' | 'support'; permission?: string; feature?: string };

const navItems: NavItem[] = [
  { path: '/', label: 'Dashboard', icon: HomeIcon, group: 'overview' },
  { path: '/patients', feature: 'patients', label: 'Patients', icon: UsersIcon, group: 'care', permission: 'patient.read' },
  { path: '/admissions', feature: 'patients', label: 'Admissions', icon: UserPlusIcon, group: 'care', permission: 'clinical.read' },
  { path: '/clinical-notes', feature: 'clinical_notes', label: 'Clinical Notes', icon: ClipboardDocumentListIcon, group: 'care', permission: 'clinical.read' },
  { path: '/vitals', feature: 'vitals', label: 'Vitals', icon: HeartIcon, group: 'care', permission: 'vitals.read' },
  { path: '/medications', label: 'Medication', icon: CubeIcon, group: 'care', permission: 'clinical.read' },
  { path: '/appointments', feature: 'appointments', label: 'Appointments', icon: CalendarDaysIcon, group: 'operations', permission: 'appointment.read' },
  { path: '/billing', feature: 'billing', label: 'Billing', icon: CreditCardIcon, group: 'operations', permission: 'billing.read' },
  { path: '/inventory', feature: 'inventory', label: 'Inventory', icon: CubeIcon, group: 'operations', permission: 'inventory.read' },
  { path: '/reports', feature: 'analytics', label: 'Reports', icon: ChartBarIcon, group: 'operations' },
  { path: '/staff', label: 'Staff', icon: UserGroupIcon, group: 'administration', permission: 'staff.read' },
  { path: '/settings', label: 'Settings', icon: Cog6ToothIcon, group: 'administration' },
  { path: '/help', label: 'Documentation', icon: QuestionMarkCircleIcon, group: 'support' },
];
const groups = [['OVERVIEW', 'overview'], ['PATIENT CARE', 'care'], ['OPERATIONS', 'operations'], ['ADMINISTRATION', 'administration'], ['SUPPORT', 'support']] as const;

function Brand({ compact, onNavigate }: { compact: boolean; onNavigate: () => void }) {
  const { tenantBranding, tenantName, isPlatformAdmin } = useAuth(); const logoUrl = resolveMediaUrl(tenantBranding?.logo_url); const name = tenantName || 'RehabYangu';
  return <Link to={isPlatformAdmin ? '/admin' : '/'} onClick={onNavigate} className={`flex min-w-0 items-center ${compact ? 'justify-center' : 'gap-3'}`} aria-label={`${name} dashboard`}><span className="grid h-10 w-10 shrink-0 place-items-center overflow-hidden rounded-xl bg-white text-sm font-bold shadow-card" style={{ color: 'var(--tenant-primary)' }}>{logoUrl ? <img src={logoUrl} alt="" className="h-full w-full object-contain p-1" /> : 'R'}</span>{!compact && <span className="min-w-0"><span className="block truncate text-sm font-semibold text-white">{name}</span><span className="block text-caption font-medium uppercase tracking-[.12em] text-slate-400">{isPlatformAdmin ? 'Weiraro workspace' : 'Care workspace'}</span></span>}</Link>;
}

function Navigation({ collapsed, onNavigate }: { collapsed: boolean; onNavigate: () => void }) {
  const { isSuperAdmin, isPlatformAdmin, isRehabAdmin, permissions, hasFeature } = useAuth(); const { pathname } = useLocation();
  const platformItems: NavItem[] = [{ path: '/admin', label: 'Platform overview', icon: BuildingOffice2Icon, group: 'overview' }, { path: '/admin/plans', label: 'Subscription plans', icon: CreditCardIcon, group: 'administration' }];
  const permitted = (item: NavItem) => (!item.permission || isSuperAdmin || permissions.includes(item.permission) || (item.path === '/settings' && isRehabAdmin)) && (!item.feature || isSuperAdmin || hasFeature(item.feature));
  return <nav className="flex-1 overflow-y-auto px-3 py-5" aria-label="Primary navigation">{groups.map(([label, key]) => {
    const items = (isPlatformAdmin ? platformItems : navItems).filter((item) => item.group === key && permitted(item)); if (!items.length) return null;
    return <section key={key} className="mb-6 last:mb-0" aria-label={label}>{collapsed ? <div className="mx-2 mb-3 border-t border-white/10" /> : <p className="mb-2 px-3 text-caption font-semibold tracking-[.12em] text-slate-400">{label}</p>}<div className="space-y-1">{items.map((item) => { const active = item.path === '/' ? pathname === '/' : pathname === item.path || pathname.startsWith(`${item.path}/`); return <Link key={item.path} to={item.path} onClick={onNavigate} title={collapsed ? item.label : undefined} aria-current={active ? 'page' : undefined} className={`group flex min-h-11 items-center rounded-btn px-3 text-sm font-medium transition-colors focus-visible:outline-white ${collapsed ? 'justify-center' : 'gap-3'} ${active ? 'bg-white/12 text-white shadow-[inset_3px_0_0_var(--tenant-primary)]' : 'text-slate-300 hover:bg-white/8 hover:text-white'}`}><item.icon className={`h-5 w-5 shrink-0 ${active ? 'text-white' : 'text-slate-400 group-hover:text-slate-200'}`} />{!collapsed && <span className="truncate">{item.label}</span>}</Link>; })}</div></section>;
  })}</nav>;
}

function SidebarPanel({ collapsed, close, desktop }: { collapsed: boolean; close: () => void; desktop: boolean }) {
  const { tenantName, isPlatformAdmin, displayRole } = useAuth();
  return <aside className={`${collapsed ? 'w-[76px]' : 'w-64'} flex h-full flex-col border-r border-white/10 text-slate-200 transition-[width] duration-200`} style={{ backgroundColor: 'var(--tenant-sidebar)' }}><div className={`flex h-[72px] items-center border-b border-white/10 ${collapsed ? 'justify-center px-3' : 'justify-between px-4'}`}><Brand compact={collapsed} onNavigate={close} />{!desktop && <button aria-label="Close navigation" onClick={close} className="grid h-11 w-11 place-items-center rounded-btn text-slate-200 hover:bg-white/10"><XMarkIcon className="h-5 w-5" /></button>}</div><Navigation collapsed={collapsed} onNavigate={close} />{!collapsed && <div className="border-t border-white/10 p-4"><p className="truncate text-sm font-medium text-white">{tenantName || 'RehabYangu'}</p><p className="mt-0.5 text-caption font-medium text-slate-400">{isPlatformAdmin ? 'Platform administration' : displayRole}</p></div>}</aside>;
}

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false); const [mobileOpen, setMobileOpen] = useState(false); const { pathname } = useLocation(); const { isPlatformAdmin, isSuperAdmin, hasFeature } = useAuth();
  const mobileItems = isPlatformAdmin ? [{ path: '/admin', label: 'Admin', icon: BuildingOffice2Icon, group: 'overview' as const }, { path: '/admin/plans', label: 'Plans', icon: CreditCardIcon, group: 'administration' as const }] : navItems.filter((item) => ['/', '/patients', '/appointments', '/billing'].includes(item.path) && (!item.feature || isSuperAdmin || hasFeature(item.feature)));
  return <><div className={`${collapsed ? 'w-[76px]' : 'w-64'} hidden shrink-0 lg:block`}><div className="fixed inset-y-0 left-0"><SidebarPanel collapsed={collapsed} close={() => undefined} desktop /><button aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'} onClick={() => setCollapsed((value) => !value)} className="absolute -right-3 top-[94px] grid h-7 w-7 place-items-center rounded-full border border-border bg-surface text-ink-secondary shadow-card hover:text-primary">{collapsed ? <ChevronRightIcon className="h-4 w-4" /> : <ChevronLeftIcon className="h-4 w-4" />}</button></div></div><button aria-label="Open navigation" onClick={() => setMobileOpen(true)} className="fixed left-3 top-3 z-30 grid h-11 w-11 place-items-center rounded-btn bg-surface text-ink-primary shadow-card lg:hidden"><Bars3Icon className="h-5 w-5" /></button>{mobileOpen && <div className="fixed inset-0 z-50 lg:hidden"><button aria-label="Close navigation" onClick={() => setMobileOpen(false)} className="absolute inset-0 w-full bg-slate-950/45" /><div className="relative h-full w-72 max-w-[calc(100vw-2rem)]"><SidebarPanel collapsed={false} close={() => setMobileOpen(false)} desktop={false} /></div></div>}<nav aria-label="Mobile primary navigation" className="fixed inset-x-0 bottom-0 z-30 grid grid-cols-4 border-t border-border bg-surface/95 px-1 pb-[env(safe-area-inset-bottom)] shadow-[0_-4px_16px_rgba(15,46,61,.08)] backdrop-blur lg:hidden">{mobileItems.map((item) => { const active = item.path === '/' ? pathname === '/' : pathname.startsWith(item.path); return <Link key={item.path} to={item.path} className={`flex min-h-16 flex-col items-center justify-center gap-1 rounded-btn text-caption font-medium ${active ? 'text-primary' : 'text-ink-secondary'}`}><item.icon className="h-5 w-5" /><span>{item.label}</span></Link>; })}</nav></>;
}
