'use client';

import { useState, useTransition } from 'react';
import { signIn } from 'next-auth/react';
import { useRouter } from 'next/navigation';

type Mode = 'login' | 'signup';

export default function AuthPage() {
  const [mode, setMode] = useState<Mode>('login');
  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-md space-y-6">
        {/* Toggle */}
        <div className="flex rounded-xl border overflow-hidden">
          <button
            className={`w-1/2 py-2 text-sm font-medium ${mode === 'login' ? 'bg-gray-900 text-white' : 'bg-white'}`}
            onClick={() => setMode('login')}
          >
            Log in
          </button>
          <button
            className={`w-1/2 py-2 text-sm font-medium ${mode === 'signup' ? 'bg-gray-900 text-white' : 'bg-white'}`}
            onClick={() => setMode('signup')}
          >
            Sign up
          </button>
        </div>

        {mode === 'login' ? <LoginForm /> : <SignupForm onDone={() => setMode('login')} />}
      </div>
    </div>
  );
}

function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [err, setErr] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);

    startTransition(async () => {
      const res = await signIn('credentials', { email, password, redirect: false });
      if (res?.error) {
        setErr(res.error || 'Invalid email or password');
        return;
      }
      router.push('/'); // or '/dashboard'
      router.refresh();
    });
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div>
        <label className="block text-sm mb-1">Email</label>
        <input
          className="w-full border rounded-md px-3 py-2"
          type="email" value={email} onChange={e => setEmail(e.target.value)} required
        />
      </div>
      <div>
        <label className="block text-sm mb-1">Password</label>
        <input
          className="w-full border rounded-md px-3 py-2"
          type="password" value={password} onChange={e => setPassword(e.target.value)} required
        />
      </div>
      {err && <p className="text-sm text-red-600">{err}</p>}
      <button
        type="submit"
        className="w-full rounded-md bg-gray-900 text-white py-2 disabled:opacity-50"
        disabled={isPending}
      >
        {isPending ? 'Signing in…' : 'Sign in'}
      </button>
    </form>
  );
}

function SignupForm({ onDone }: { onDone: () => void }) {
  const router = useRouter();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [err, setErr] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);

    startTransition(async () => {
      const res = await fetch('/api/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password }),
      });
      const data = await res.json();

      if (!res.ok) {
        setErr(data?.error || 'Failed to sign up');
        return;
      }

      // Optional: auto-login after signup
      const login = await signIn('credentials', { email, password, redirect: false });
      if (login?.error) {
        // If auto-login fails, switch to login tab with no error
        onDone();
        return;
      }
      router.push('/'); // or '/dashboard'
      router.refresh();
    });
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div>
        <label className="block text-sm mb-1">Name (optional)</label>
        <input
          className="w-full border rounded-md px-3 py-2"
          type="text" value={name} onChange={e => setName(e.target.value)}
        />
      </div>
      <div>
        <label className="block text-sm mb-1">Email</label>
        <input
          className="w-full border rounded-md px-3 py-2"
          type="email" value={email} onChange={e => setEmail(e.target.value)} required
        />
      </div>
      <div>
        <label className="block text-sm mb-1">Password</label>
        <input
          className="w-full border rounded-md px-3 py-2"
          type="password" value={password} onChange={e => setPassword(e.target.value)} required
        />
      </div>
      {err && <p className="text-sm text-red-600">{err}</p>}
      <button
        type="submit"
        className="w-full rounded-md bg-gray-900 text-white py-2 disabled:opacity-50"
        disabled={isPending}
      >
        {isPending ? 'Creating account…' : 'Create account'}
      </button>
    </form>
  );
}
