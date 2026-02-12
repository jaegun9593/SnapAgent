import { Link } from 'react-router-dom';
import { User, LogOut } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';

export function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="h-16 border-b border-border bg-card px-6 flex items-center justify-between">
      <div className="flex items-center space-x-4">
        <h2 className="text-lg font-semibold">RAG Agent Builder</h2>
      </div>
      <div className="flex items-center space-x-3">
        <span className="text-sm text-muted-foreground">{user?.email}</span>
        <Button variant="ghost" size="sm" asChild>
          <Link to="/mypage" className="inline-flex items-center">
            <User className="mr-1.5 h-4 w-4 shrink-0" />
            마이페이지
          </Link>
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => logout()}
          className="text-destructive hover:text-destructive"
        >
          <LogOut className="mr-1.5 h-4 w-4" />
          로그아웃
        </Button>
      </div>
    </header>
  );
}
