import { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { RefreshCw, Check, X } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useAuthStore } from '@/stores/authStore';
import { authService } from '@/services/authService';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

interface PasswordRule {
  key: string;
  label: string;
  test: (pw: string, email: string) => boolean;
}

const PASSWORD_RULES: PasswordRule[] = [
  {
    key: 'length',
    label: '8자 이상 (2종 조합 시 10자 이상)',
    test: (pw) => {
      const types = [/[A-Z]/, /[a-z]/, /[0-9]/, /[!@#$%^&*()\-_=+\[\]{}|;:'",.<>?/`~\\]/];
      const count = types.filter((r) => r.test(pw)).length;
      if (count >= 3) return pw.length >= 8;
      if (count === 2) return pw.length >= 10;
      return false;
    },
  },
  {
    key: 'types',
    label: '영문 대/소문자, 숫자, 특수문자 중 2종 이상 포함',
    test: (pw) => {
      const types = [/[A-Z]/, /[a-z]/, /[0-9]/, /[!@#$%^&*()\-_=+\[\]{}|;:'",.<>?/`~\\]/];
      return types.filter((r) => r.test(pw)).length >= 2;
    },
  },
  {
    key: 'noRepeat',
    label: '동일 문자 3회 이상 연속 금지',
    test: (pw) => {
      for (let i = 0; i < pw.length - 2; i++) {
        if (pw[i] === pw[i + 1] && pw[i + 1] === pw[i + 2]) return false;
      }
      return true;
    },
  },
  {
    key: 'noSequential',
    label: '연속된 순차 문자/숫자 3자 이상 금지 (abc, 321)',
    test: (pw) => {
      for (let i = 0; i < pw.length - 2; i++) {
        const c0 = pw.charCodeAt(i);
        const c1 = pw.charCodeAt(i + 1);
        const c2 = pw.charCodeAt(i + 2);
        if (c1 - c0 === 1 && c2 - c1 === 1) return false;
        if (c0 - c1 === 1 && c1 - c2 === 1) return false;
      }
      return true;
    },
  },
  {
    key: 'noEmail',
    label: '이메일 아이디 포함 금지',
    test: (pw, email) => {
      if (!email) return true;
      const local = email.split('@')[0]?.toLowerCase();
      if (!local || local.length < 4) return true;
      return !pw.toLowerCase().includes(local);
    },
  },
];

export function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [captchaId, setCaptchaId] = useState('');
  const [captchaImage, setCaptchaImage] = useState('');
  const [captchaText, setCaptchaText] = useState('');
  const [captchaLoading, setCaptchaLoading] = useState(false);
  const [confirmError, setConfirmError] = useState('');
  const { register, registerError, isRegisterPending } = useAuth();
  const navigate = useNavigate();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  const passwordResults = useMemo(
    () => PASSWORD_RULES.map((rule) => ({
      ...rule,
      passed: password.length > 0 && rule.test(password, email),
    })),
    [password, email]
  );
  const allPasswordValid = password.length > 0 && passwordResults.every((r) => r.passed);

  const loadCaptcha = useCallback(async () => {
    setCaptchaLoading(true);
    setCaptchaText('');
    try {
      const res = await authService.getCaptcha();
      setCaptchaId(res.captcha_id);
      setCaptchaImage(res.image_base64);
    } catch {
      // silently fail, user can retry
    } finally {
      setCaptchaLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    loadCaptcha();
  }, [loadCaptcha]);

  // Reload CAPTCHA on register failure (consumed CAPTCHA)
  useEffect(() => {
    if (registerError) {
      loadCaptcha();
    }
  }, [registerError, loadCaptcha]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setConfirmError('');

    if (!allPasswordValid) return;

    if (password !== confirmPassword) {
      setConfirmError('비밀번호가 일치하지 않습니다');
      return;
    }

    register(
      {
        email,
        password,
        full_name: fullName,
        captcha_id: captchaId,
        captcha_text: captchaText,
      },
      {
        onSuccess: () => {
          navigate('/dashboard');
        },
      }
    );
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="w-full max-w-md p-8 space-y-6 bg-card border border-border rounded-lg">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-primary">SnapAgent</h1>
          <p className="text-sm text-muted-foreground mt-2">
            새 계정을 만드세요
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="fullName">이름</Label>
            <Input
              id="fullName"
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="이름을 입력하세요"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">이메일</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="이메일을 입력하세요"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">비밀번호</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="비밀번호를 입력하세요"
              required
            />
            {password.length > 0 && (
              <ul className="space-y-1 mt-1">
                {passwordResults.map((r) => (
                  <li key={r.key} className="flex items-center gap-1.5 text-xs">
                    {r.passed ? (
                      <Check className="h-3 w-3 text-green-500 shrink-0" />
                    ) : (
                      <X className="h-3 w-3 text-destructive shrink-0" />
                    )}
                    <span className={r.passed ? 'text-green-600' : 'text-destructive'}>
                      {r.label}
                    </span>
                  </li>
                ))}
              </ul>
            )}
            {password.length === 0 && (
              <p className="text-xs text-muted-foreground">
                영문 대/소문자, 숫자, 특수문자 중 3종 포함 시 8자, 2종 포함 시 10자 이상
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="confirmPassword">비밀번호 확인</Label>
            <Input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => {
                setConfirmPassword(e.target.value);
                setConfirmError('');
              }}
              placeholder="비밀번호를 다시 입력하세요"
              required
            />
            {confirmError && (
              <p className="text-xs text-destructive">{confirmError}</p>
            )}
            {!confirmError && confirmPassword.length > 0 && password !== confirmPassword && (
              <p className="text-xs text-destructive">비밀번호가 일치하지 않습니다</p>
            )}
            {confirmPassword.length > 0 && password === confirmPassword && (
              <p className="text-xs text-green-600 flex items-center gap-1">
                <Check className="h-3 w-3" /> 비밀번호가 일치합니다
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label>보안 문자</Label>
            <div className="flex items-center gap-2">
              {captchaImage ? (
                <img
                  src={captchaImage}
                  alt="CAPTCHA"
                  className="h-[46px] rounded border border-border select-none pointer-events-none"
                  draggable={false}
                />
              ) : (
                <div className="h-[46px] w-[140px] rounded border border-border bg-muted flex items-center justify-center">
                  <span className="text-xs text-muted-foreground">로딩 중...</span>
                </div>
              )}
              <Button
                type="button"
                variant="outline"
                size="icon"
                onClick={loadCaptcha}
                disabled={captchaLoading}
                className="shrink-0"
              >
                <RefreshCw className={`h-4 w-4 ${captchaLoading ? 'animate-spin' : ''}`} />
              </Button>
            </div>
            <Input
              value={captchaText}
              onChange={(e) => setCaptchaText(e.target.value.toUpperCase())}
              placeholder="위 이미지의 문자를 입력하세요"
              className="uppercase"
              required
            />
          </div>

          {registerError && (
            <p className="text-sm text-destructive">
              회원가입에 실패했습니다. 다시 시도해주세요.
            </p>
          )}

          <Button type="submit" className="w-full" disabled={isRegisterPending}>
            {isRegisterPending ? '가입 중...' : '회원가입'}
          </Button>
        </form>

        <p className="text-center text-sm text-muted-foreground">
          이미 계정이 있으신가요?{' '}
          <Link to="/login" className="text-primary hover:underline">
            로그인
          </Link>
        </p>
      </div>
    </div>
  );
}
