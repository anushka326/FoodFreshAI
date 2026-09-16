import React, { useState } from 'react';
import { BRANDING_ASSETS } from '../../assets/branding/index.js';
import { FOOD_ASSETS } from '../../assets/food/index.js';
import { authService } from '../../services/authService.js';

export function LoginPage({ navigate }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage('');

    try {
      await authService.login(email, password);
      sessionStorage.removeItem('foodfresh_dashboard_welcome_seen');
      navigate('/dashboard');
    } catch (err) {
      setErrorMessage(err.message || 'Invalid credentials. Please verify and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-surface flex flex-col justify-center items-center p-4 sm:p-6 md:p-8 font-sans">
      {/* Container Card */}
      <div className="w-full max-w-5xl bg-white rounded-3xl shadow-xl overflow-hidden border border-surface-container-high/60 grid grid-cols-1 lg:grid-cols-12 min-h-[640px]">
        {/* Left Visual Brand Column (5 cols) */}
        <div className="relative hidden lg:flex lg:col-span-5 flex-col justify-between p-10 overflow-hidden bg-primary text-white">
          {/* Background produce image with deep emerald overlay */}
          <div className="absolute inset-0 z-0">
            <img
              src={FOOD_ASSETS.pantryProduceHero}
              alt="Fresh kitchen produce"
              className="w-full h-full object-cover opacity-25 mix-blend-overlay"
            />
            <div className="absolute inset-0 bg-gradient-to-b from-primary/95 via-primary/85 to-primary" />
          </div>

          {/* Brand header */}
          <div className="relative z-10">
            <button
              type="button"
              onClick={() => navigate('/')}
              className="flex items-center gap-2.5 text-left group cursor-pointer"
            >
              <div className="w-9 h-9 rounded-xl bg-white/10 backdrop-blur-sm border border-white/20 flex items-center justify-center p-1.5">
                <img src={BRANDING_ASSETS.logoUrl} alt="FoodFresh AI" className="w-full h-full object-contain" />
              </div>
              <div>
                <span className="font-extrabold text-lg text-white tracking-tight leading-tight block">
                  FoodFresh <span className="text-secondary-container">AI</span>
                </span>
                <span className="text-[10px] text-white/80 font-medium tracking-wide">
                  Know. Save. Waste Less.
                </span>
              </div>
            </button>
          </div>

          {/* Central value pillars */}
          <div className="relative z-10 my-auto space-y-6">
            <h2 className="text-2xl font-bold tracking-tight text-white leading-tight">
              Smarter food habits start right here on your kitchen counter.
            </h2>

            <div className="space-y-4 text-xs">
              <div className="flex items-start gap-3 p-3 rounded-2xl bg-white/10 backdrop-blur-xs border border-white/15">
                <span className="text-lg">🌿</span>
                <div>
                  <p className="font-bold text-white">Visual Freshness Scoring</p>
                  <p className="text-white/80">Computer vision evaluates skin integrity and cellular quality.</p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3 rounded-2xl bg-white/10 backdrop-blur-xs border border-white/15">
                <span className="text-lg">🥇</span>
                <div>
                  <p className="font-bold text-white">Eat First Priority Engine</p>
                  <p className="text-white/80">Never let ripe vine tomatoes or bananas slip past their culinary peak.</p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3 rounded-2xl bg-white/10 backdrop-blur-xs border border-white/15">
                <span className="text-lg">🌱</span>
                <div>
                  <p className="font-bold text-white">FreshoBuddy AI Assistant</p>
                  <p className="text-white/80">Tailored storage advice, ethylene gas guides, and quick rescue tips.</p>
                </div>
              </div>
            </div>
          </div>

          {/* Footer quote */}
          <div className="relative z-10 text-[11px] text-white/70 italic border-t border-white/10 pt-4">
            “A mindful kitchen begins with conscious food decisions.”
          </div>
        </div>

        {/* Right Form Column (7 cols) */}
        <div className="lg:col-span-7 p-6 sm:p-10 md:p-12 flex flex-col justify-between bg-surface-container-lowest">
          {/* Top Bar with Home return */}
          <div className="flex items-center justify-between pb-6">
            <button
              type="button"
              onClick={() => navigate('/')}
              className="flex items-center gap-1.5 text-xs font-semibold text-on-surface-variant hover:text-primary transition-colors cursor-pointer"
            >
              <span className="material-symbols-outlined text-[16px]">arrow_back</span>
              <span>Back to Home</span>
            </button>
          </div>

          {/* Form Header */}
          <div className="max-w-md w-full mx-auto my-auto">
            <div className="mb-8">
              <h1 className="text-2xl sm:text-3xl font-extrabold text-primary tracking-tight">
                Welcome back, Chef
              </h1>
              <p className="text-xs sm:text-sm text-on-surface-variant mt-1.5">
                Sign in to manage your kitchen freshness logs and Eat First priorities.
              </p>
            </div>

            {/* Error Message banner */}
            {errorMessage && (
              <div className="mb-6 p-4 rounded-2xl bg-error-container text-on-error-container text-xs flex items-start gap-3 border border-red-200">
                <span className="material-symbols-outlined text-[20px] text-error shrink-0">error</span>
                <div className="flex-1">
                  <p className="font-bold">Authentication Notice</p>
                  <p className="mt-0.5">{errorMessage}</p>
                </div>
                <button
                  type="button"
                  onClick={() => setErrorMessage('')}
                  className="text-error font-bold"
                >
                  ✕
                </button>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Email */}
              <div>
                <label className="block text-xs font-bold text-on-surface mb-1.5" htmlFor="login-email">
                  Email Address
                </label>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-3.5 top-3 text-on-surface-variant text-[18px]">
                    mail
                  </span>
                  <input
                    id="login-email"
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your email address"
                    className="w-full pl-10 pr-4 py-3 bg-surface-container-low/60 border border-surface-container-high rounded-2xl text-xs sm:text-sm text-on-surface placeholder:text-outline focus:outline-none focus:ring-2 focus:ring-secondary/50 focus:bg-white transition-all"
                  />
                </div>
              </div>

              {/* Password */}
              <div>
                <div className="flex justify-between items-center mb-1.5">
                  <label className="block text-xs font-bold text-on-surface" htmlFor="login-password">
                    Password
                  </label>
                  <button
                    type="button"
                    onClick={() => setErrorMessage('Password recovery will be available when account services are connected.')}
                    className="text-[11px] font-semibold text-secondary hover:underline cursor-pointer"
                  >
                    Forgot password?
                  </button>
                </div>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-3.5 top-3 text-on-surface-variant text-[18px]">
                    lock
                  </span>
                  <input
                    id="login-password"
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    className="w-full pl-10 pr-11 py-3 bg-surface-container-low/60 border border-surface-container-high rounded-2xl text-xs sm:text-sm text-on-surface placeholder:text-outline focus:outline-none focus:ring-2 focus:ring-secondary/50 focus:bg-white transition-all"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3.5 top-3 text-on-surface-variant hover:text-on-surface cursor-pointer"
                    aria-label="Toggle password visibility"
                  >
                    <span className="material-symbols-outlined text-[18px]">
                      {showPassword ? 'visibility_off' : 'visibility'}
                    </span>
                  </button>
                </div>
              </div>

              {/* Remember Me */}
              <div className="flex items-center justify-between pt-1">
                <label className="flex items-center gap-2.5 cursor-pointer text-xs font-medium text-on-surface-variant">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 rounded-md text-secondary border-surface-container-high focus:ring-secondary"
                  />
                  <span>Keep me signed in on this device</span>
                </label>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3.5 px-6 rounded-full bg-primary hover:bg-primary-container text-white font-bold text-sm shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 active:scale-98 disabled:opacity-60 cursor-pointer mt-4"
              >
                {loading ? (
                  <>
                    <span className="w-4 h-4 rounded-full border-2 border-white/40 border-t-white animate-spin" />
                    <span>Signing In…</span>
                  </>
                ) : (
                  <>
                    <span>Sign In to Kitchen</span>
                    <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
                  </>
                )}
              </button>
            </form>

            {/* Link to Register */}
            <p className="text-center text-xs text-on-surface-variant mt-6">
              New to FoodFresh AI?{' '}
              <button
                type="button"
                onClick={() => navigate('/register')}
                className="font-bold text-secondary hover:underline cursor-pointer"
              >
                Create your kitchen account
              </button>
            </p>
          </div>

          <div className="pt-6 text-center text-[11px] text-outline">
            Protected by FoodFresh AI Privacy Standards.
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
