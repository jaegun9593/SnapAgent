import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from '@/lib/queryClient';
import { Toaster } from '@/components/ui/sonner';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { MainLayout } from '@/components/layout/MainLayout';
import { LoginPage } from '@/pages/LoginPage';
import { RegisterPage } from '@/pages/RegisterPage';
import { MyAgentsPage } from '@/pages/MyAgentsPage';
import { AgentChatPage } from '@/pages/AgentChatPage';
import { AgentCreatePage } from '@/pages/AgentCreatePage';
import { AgentEditPage } from '@/pages/AgentEditPage';
import { TemplatesPage } from '@/pages/TemplatesPage';
import { DashboardPage } from '@/pages/DashboardPage';
import { MyPage } from '@/pages/MyPage';
import { MyPageEdit } from '@/pages/MyPageEdit';

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected routes */}
          <Route element={<ProtectedRoute />}>
            <Route element={<MainLayout />}>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/agents" element={<MyAgentsPage />} />
              <Route path="/agents/create" element={<AgentCreatePage />} />
              <Route path="/agents/:id/edit" element={<AgentEditPage />} />
              <Route path="/agents/:id/chat" element={<AgentChatPage />} />
              <Route path="/templates" element={<TemplatesPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/mypage" element={<MyPage />} />
              <Route path="/mypage/edit" element={<MyPageEdit />} />
            </Route>
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
      <Toaster />
    </QueryClientProvider>
  );
}

export default App;
