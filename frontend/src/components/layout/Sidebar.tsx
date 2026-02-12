import { Link, useLocation } from 'react-router-dom';
import { Bot, Plus, LayoutTemplate, BarChart3 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface NavItem {
  name: string;
  path: string;
  icon: React.ReactNode;
}

const navItems: NavItem[] = [
  { name: '내 Agent', path: '/agents', icon: <Bot className="h-4 w-4" /> },
  { name: 'Agent 생성', path: '/agents/create', icon: <Plus className="h-4 w-4" /> },
  { name: '템플릿', path: '/templates', icon: <LayoutTemplate className="h-4 w-4" /> },
  { name: '대시보드', path: '/dashboard', icon: <BarChart3 className="h-4 w-4" /> },
];

export function Sidebar() {
  const location = useLocation();

  return (
    <aside className="w-64 bg-card border-r border-border min-h-screen">
      <div className="p-6">
        <Link to="/agents">
          <h1 className="text-2xl font-bold text-primary hover:opacity-80 transition-opacity cursor-pointer">
            SnapAgent
          </h1>
        </Link>
        <p className="text-xs text-muted-foreground mt-1">RAG Agent Builder</p>
      </div>
      <nav className="px-4 space-y-1">
        {navItems.map((item) => {
          const isActive =
            location.pathname === item.path ||
            (item.path !== '/agents/create' &&
              location.pathname.startsWith(item.path + '/'));
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
