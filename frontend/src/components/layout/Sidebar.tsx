import { Link, useLocation } from 'react-router-dom';
import { Bot, Plus, LayoutTemplate, BarChart3 } from 'lucide-react';
import { cn } from '@/lib/utils';

function SidebarLogo({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none" className={className}>
      <rect width="64" height="64" rx="14" fill="#1e40af"/>
      <defs>
        <linearGradient id="sidebar-mane" x1="0.2" y1="0" x2="0.8" y2="1">
          <stop offset="0%" stopColor="#ff69b4"/>
          <stop offset="25%" stopColor="#87ceeb"/>
          <stop offset="55%" stopColor="#ffd700"/>
          <stop offset="80%" stopColor="#ff8c00"/>
          <stop offset="100%" stopColor="#32cd32"/>
        </linearGradient>
        <linearGradient id="sidebar-manePastel" x1="0.2" y1="0" x2="0.8" y2="1">
          <stop offset="0%" stopColor="#ffb6d9"/>
          <stop offset="25%" stopColor="#b8e4f9"/>
          <stop offset="55%" stopColor="#fff0a0"/>
          <stop offset="80%" stopColor="#ffc470"/>
          <stop offset="100%" stopColor="#90ee90"/>
        </linearGradient>
      </defs>
      <path d="M 44 11 Q 50 6, 57 11" stroke="#ff69b4" strokeWidth="1.8" strokeLinecap="round" fill="none"/>
      <path d="M 44 13.5 Q 50 8.5, 57 13.5" stroke="#87ceeb" strokeWidth="1.8" strokeLinecap="round" fill="none"/>
      <path d="M 44 16 Q 50 11, 57 16" stroke="#ffd700" strokeWidth="1.8" strokeLinecap="round" fill="none"/>
      <path d="M 44 18.5 Q 50 13.5, 57 18.5" stroke="#32cd32" strokeWidth="1.8" strokeLinecap="round" fill="none"/>
      <path d="M 30 14 C 38 8, 50 12, 52 24 C 54 36, 48 48, 40 52 C 34 54, 32 50, 34 44 C 36 38, 38 30, 38 24 C 38 18, 36 14, 30 14 Z" fill="url(#sidebar-mane)" stroke="#db2777" strokeWidth="1.5"/>
      <path d="M 32 16 C 38 12, 46 18, 48 26 C 50 34, 46 44, 40 48 C 36 50, 36 46, 36 42 C 36 36, 40 28, 40 22 C 40 18, 36 16, 32 16 Z" fill="url(#sidebar-manePastel)"/>
      <path d="M 32 16 L 34 5 L 38 16 Z" fill="#e8e8e8" stroke="#db2777" strokeWidth="0.8"/>
      <path d="M 33 15 L 35 7 L 37 15 Z" fill="#f9a8d4" opacity="0.6"/>
      <path d="M 24 12 C 20 16, 12 26, 6 36 C 3 42, 5 48, 12 50 C 20 52, 28 48, 32 42 C 36 36, 38 28, 36 20 C 34 14, 28 12, 24 12 Z" fill="#f9a8d4"/>
      <path d="M 24 14 C 20 18, 12 28, 8 36 C 6 40, 8 44, 12 46 C 18 48, 24 46, 28 42 C 32 38, 34 32, 34 26 C 34 20, 30 16, 26 14 Z" fill="white"/>
      <path d="M 26 16 L 23 4 L 30 14 Z" fill="white" stroke="#db2777" strokeWidth="1"/>
      <path d="M 27 15 L 24.5 6 L 29 14 Z" fill="#f9a8d4"/>
      <path d="M 27 7 L 29 -1 L 32 7 Z" fill="#fbbf24"/>
      <path d="M 28 7 L 29.5 1 L 31 7 Z" fill="#fde68a"/>
      <line x1="28.5" y1="4" x2="30.5" y2="6.5" stroke="#d97706" strokeWidth="0.8"/>
      <line x1="29" y1="2" x2="30" y2="4.5" stroke="#d97706" strokeWidth="0.6"/>
      <ellipse cx="20" cy="24" rx="3" ry="3.5" fill="#1e1b4b"/>
      <circle cx="18.8" cy="22.8" r="1.3" fill="white"/>
      <circle cx="21" cy="25" r="0.6" fill="white" fillOpacity="0.5"/>
      <ellipse cx="9" cy="40" rx="1" ry="1.3" fill="#e0d0d0"/>
      <path d="M 10 44 Q 14 46, 18 44" stroke="#e0c0c0" strokeWidth="0.8" strokeLinecap="round" fill="none"/>
      <circle cx="50" cy="52" r="1.2" fill="#ffd700" fillOpacity="0.7"/>
      <circle cx="56" cy="46" r="0.8" fill="#ff69b4" fillOpacity="0.5"/>
      <circle cx="8" cy="56" r="0.8" fill="#87ceeb" fillOpacity="0.5"/>
      <circle cx="4" cy="10" r="0.6" fill="#ffd700" fillOpacity="0.4"/>
    </svg>
  );
}

interface NavItem {
  name: string;
  path: string;
  icon: React.ReactNode;
}

const navItems: NavItem[] = [
  { name: '대시보드', path: '/dashboard', icon: <BarChart3 className="h-4 w-4" /> },
  { name: '내 Agent', path: '/agents', icon: <Bot className="h-4 w-4" /> },
  { name: 'Agent 생성', path: '/agents/create', icon: <Plus className="h-4 w-4" /> },
  { name: '템플릿', path: '/templates', icon: <LayoutTemplate className="h-4 w-4" /> },
];

export function Sidebar() {
  const location = useLocation();

  return (
    <aside className="w-64 bg-card border-r border-border min-h-screen">
      <div className="p-6">
        <Link to="/dashboard" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
          <SidebarLogo className="h-9 w-9 shrink-0" />
          <div>
            <h1 className="text-2xl font-bold text-primary">
              SnapAgent
            </h1>
            <p className="text-xs text-muted-foreground">RAG Agent Builder</p>
          </div>
        </Link>
      </div>
      <nav className="px-4 space-y-1">
        {navItems.map((item) => {
          // Exact match, or child route match excluding sibling nav paths
          const isActive =
            location.pathname === item.path ||
            (location.pathname.startsWith(item.path + '/') &&
              !navItems.some(
                (other) =>
                  other.path !== item.path &&
                  other.path.startsWith(item.path + '/') &&
                  location.pathname.startsWith(other.path)
              ));
          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                'flex items-center gap-3 px-4 py-2 rounded-md text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              )}
            >
              {item.icon}
              {item.name}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
