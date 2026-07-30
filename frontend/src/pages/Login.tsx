import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from '@tanstack/react-router';
import { EnvelopeIcon, LockClosedIcon } from '@heroicons/react/24/outline';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      await login(username, password);
      navigate({ to: '/' });
    } catch (err) {
      setError('Invalid credentials. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#f4f6f7] px-4 py-12">
      <div className="w-full max-w-sm">
        {/* Logo / Brand */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-primary-700">RehabYangu</h1>
          <p className="text-sm text-secondary-500 mt-1">Smart Rehabilitation Management</p>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-xl shadow-card p-6">
          <h2 className="text-xl font-semibold text-secondary-800 mb-2">Welcome back</h2>
          <p className="text-sm text-secondary-500 mb-6">Sign in to your account to continue.</p>

          <form onSubmit={handleSubmit}>
            <div className="space-y-4">
              <div>
                <label className="form-label">Username</label>
                <div className="relative">
                  <EnvelopeIcon className="w-4 h-4 text-secondary-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="input-field pl-9"
                    placeholder="Enter your username"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="form-label">Password</label>
                <div className="relative">
                  <LockClosedIcon className="w-4 h-4 text-secondary-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="input-field pl-9"
                    placeholder="Enter your password"
                    required
                  />
                </div>
              </div>

              {error && (
                <div className="text-sm text-danger bg-danger-light p-2 rounded-md">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={isLoading}
                className="btn-primary w-full justify-center py-2.5 text-sm font-semibold"
              >
                {isLoading ? 'Signing in...' : 'Sign in'}
              </button>

              <div className="text-center text-xs text-secondary-400 pt-2">
                <span>© 2026 RehabYangu. Powered by Weiraro Technologies.</span>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;
