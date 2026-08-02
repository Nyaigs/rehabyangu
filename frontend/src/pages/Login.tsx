import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from '@tanstack/react-router';
import Logo from '../components/auth/Logo';
import InputField from '../components/auth/InputField';
import PasswordField from '../components/auth/PasswordField';
import Button from '../components/auth/Button';
import SecurityNotice from '../components/auth/SecurityNotice';
import Footer from '../components/auth/Footer';
import { EnvelopeIcon } from '@heroicons/react/24/outline';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(username, password);
      navigate({ to: '/' });
    } catch (err) {
      setError('Unable to sign in. Please check your email and password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-[#f4f6f7]">
      {/* Left Brand Section */}
      <div className="md:w-[45%] bg-[#0f2e3d] text-white relative overflow-hidden flex flex-col justify-between p-8 md:p-12 lg:p-16 min-h-[50vh] md:min-h-screen">
        {/* Subtle gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-[#0f2e3d] via-[#1d5a70]/30 to-[#0f2e3d] opacity-15" />

        {/* Logo */}
        <div className="relative z-10 animate-fadeIn" style={{ animationDelay: '100ms' }}>
          <Logo size="lg" className="opacity-90" />
        </div>

        {/* Brand Text */}
        <div className="relative z-10 flex-1 flex flex-col justify-center max-w-md mx-auto md:mx-0">
          <h1 className="text-3xl md:text-4xl font-bold leading-tight animate-slideUp" style={{ animationDelay: '200ms' }}>
            Transforming Rehabilitation Care Through Technology
          </h1>
          <p className="text-[#dce8ec] text-sm md:text-base leading-relaxed mt-4 max-w-sm animate-slideUp" style={{ animationDelay: '400ms' }}>
            A secure digital platform helping rehabilitation centres manage patients, clinical workflows, billing, and operations in one place.
          </p>

          {/* Illustration placeholder */}
          <div className="mt-8 relative animate-float">
            <div className="w-full max-w-sm h-48 bg-[#1d5a70]/30 rounded-2xl flex items-center justify-center border border-[#1d5a70]/20">
              <svg className="w-24 h-24 text-[#dce8ec]/30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4" />
              </svg>
            </div>
          </div>
        </div>

        {/* Footer (only visible on desktop) */}
        <div className="relative z-10 hidden md:block">
          <Footer />
        </div>
      </div>

      {/* Right Login Section */}
      <div className="md:w-[55%] flex items-center justify-center p-6 md:p-12 bg-[#f4f6f7]">
        <div className="w-full max-w-md animate-slideUp" style={{ animationDelay: '300ms' }}>
          <div className="bg-white rounded-2xl shadow-card p-6 md:p-10">
            {/* Small logo on mobile/tablet */}
            <div className="md:hidden flex justify-center mb-4">
              <Logo size="sm" />
            </div>

            <div className="text-center md:text-left">
              <h2 className="text-2xl md:text-3xl font-bold text-secondary-800">Welcome Back</h2>
              <p className="text-sm text-secondary-500 mt-1">Sign in to access your rehabilitation workspace.</p>
            </div>

            <form onSubmit={handleSubmit} className="mt-6 space-y-4">
              <InputField
                label="Username"
                type="text"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                icon={<EnvelopeIcon className="w-5 h-5" />}
                error={error}
                required
              />

              <PasswordField
                label="Password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                error={error}
                required
              />

              <Button type="submit" loading={loading} icon className="w-full">
                Sign in
              </Button>
            </form>

            <div className="mt-6">
              <SecurityNotice />
            </div>

            {/* Footer for mobile */}
            <div className="mt-8 block md:hidden">
              <Footer />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
