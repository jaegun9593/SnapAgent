import { cn } from '@/lib/utils';

interface LoadingIndicatorProps {
  className?: string;
}

export function LoadingIndicator({ className }: LoadingIndicatorProps) {
  return (
    <div className={cn('flex items-center gap-1', className)}>
      <span className="inline-block h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.3s]" />
      <span className="inline-block h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.15s]" />
      <span className="inline-block h-2 w-2 animate-bounce rounded-full bg-muted-foreground" />
    </div>
  );
}
