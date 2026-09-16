import React, { useState } from 'react';
import { BRANDING_ASSETS } from '../../assets/branding/index.js';
import { FOOD_ASSETS } from '../../assets/food/index.js';
import { authService } from '../../services/authService.js';

export function RegisterPage({ navigate }) {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [householdType, setHouseholdType] = useState('');
  const [agreeTerms, setAgreeTerms] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!fullName.trim()) {
      setErrorMessage('Please enter your name or kitchen title.');
      return;
    }
    if (!email.trim()) {
      setErrorMessage('Please enter your email address.');
      return;
    }
    if (!password) {
      setErrorMessage('Please create a password.');
      return;
    }
    if (password !== confirmPassword) {
      setErrorMessage('Passwords do not match. Please verify.');
      return;
    }
    if (!agreeTerms) {
      setErrorMessage('Please accept the Terms of Service to create your kitchen account.');
      return;
    }

    setLoading(true);
    setErrorMessage('');

    try {
      await authService.register({
        fullName: fullName.trim(),
        email: email.trim(),
        password,
        householdType,
      });
      sessionStorage.removeItem('foodfresh_dashboard_welcome_seen');
      navigate('/dashboard');
    } catch (err) {
      setErrorMessage(err.message || 'Registration encountered an issue.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-surface flex flex-col justify-center items-center p-4 sm:p-6 md:p-8 font-sans">
      <div className="w-full max-w-5xl bg-white rounded-3xl shadow-xl overflow-hidden border border-surface-container-high/60 grid grid-cols-1 lg:grid-cols-12 min-h-[680px]">
        {/* Left Visual Brand Column (5 cols) */}
        <div className="relative hidden lg:flex lg:col-span-5 flex-col justify-between p-10 overflow-hidden bg-primary text-white">
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

          {/* Central perks */}
          <div className="relative z-10 my-auto space-y-5">
            <h2 className="text-2xl font-bold tracking-tight text-white leading-tight">
              Join thousands of conscious home chefs reducing household food waste.
            </h2>

            <div className="space-y-3.5 text-xs">
              <div className="flex items-start gap-3 p-3 rounded-2xl bg-white/10 backdrop-blur-xs border border-white/15">
                <span className="text-lg">📊</span>
                <div>
                  <p className="font-bold text-white">Continuous Freshness Tracking</p>
                  <p className="text-white/80">Log your counter produce and monitor quality windows in real-time.</p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3 rounded-2xl bg-white/10 backdrop-blur-xs border border-white/15">
                <span className="text-lg">🔔</span>
                <div>
                  <p className="font-bold text-white">Smart Expiry Reminders</p>
                  <p className="text-white/80">Gentle notifications before delicate produce slips past its culinary prime.</p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3 rounded-2xl bg-white/10 backdrop-blur-xs border border-white/15">
                <span className="text-lg">🌿</span>
                <div>
                  <p className="font-bold text-white">Ethylene Gas Chemistry Guides</p>
                  <p className="text-white/80">Understand how storing apples next to greens impacts cellular aging.</p>
                </div>
              </div>
            </div>
          </div>

          <div className="relative z-10 text-[11px] text-white/70 italic border-t border-white/10 pt-4">
            “Small decisions today prevent waste tomorrow.”
          </div>
        </div>

        {/* Right Form Column (7 cols) */}
        <div className="lg:col-span-7 p-6 sm:p-10 md:p-12 flex flex-col justify-between bg-surface-container-lowest overflow-y-auto">
          {/* Top Bar */}
          <div className="flex items-center justify-between pb-4">
            <button
              type="button"
              onClick={() => navigate('/')}
              className="flex items-center gap-1.5 text-xs font-semibold text-on-surface-variant hover:text-primary transition-colors cursor-pointer"
            >
              <span className="material-symbols-outlined text-[16px]">arrow_back</span>
              <span>Back to Home</span>
            </button>
            <span className="text-xs text-on-surface-variant font-medium">Free Pantry Plan</span>
          </div>

          {/* Form Content */}
          <div className="max-w-md w-full mx-auto my-auto py-4">
            <div className="mb-6">
              <h1 className="text-2xl sm:text-3xl font-extrabold text-primary tracking-tight">
                Create Kitchen Account
              </h1>
              <p className="text-xs sm:text-sm text-on-surface-variant mt-1">
                Start tracking freshness and organizing your Eat First roadmap.
              </p>
            </div>

            {/* Error Message */}
            {errorMessage && (
              <div className="mb-4 p-3.5 rounded-2xl bg-error-container text-on-error-container text-xs flex items-center justify-between border border-red-200">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-[18px]">error</span>
                  <span>{errorMessage}</span>
                </div>
                <button
                  type="button"
                  onClick={() => setErrorMessage('')}
                  className="font-bold text-error cursor-pointer"
                >
                  ✕
                </button>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-3.5">
              {/* Full Name */}
              <div>
                <label className="block text-xs font-bold text-on-surface mb-1" htmlFor="reg-name">
                  Full Name / Kitchen Title
                </label>
                <input
                  id="reg-name"
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Enter your name"
                  className="w-full px-4 py-2.5 bg-surface-container-low/60 border border-surface-container-high rounded-2xl text-xs sm:text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-secondary/50 focus:bg-white transition-all placeholder:text-outline"
                />
              </div>

              {/* Email */}
              <div>
                <label className="block text-xs font-bold text-on-surface mb-1" htmlFor="reg-email">
                  Email Address
                </label>
                <input
                  id="reg-email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email address"
                  className="w-full px-4 py-2.5 bg-surface-container-low/60 border border-surface-container-high rounded-2xl text-xs sm:text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-secondary/50 focus:bg-white transition-all placeholder:text-outline"
                />
              </div>

              {/* Password & Confirm */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-on-surface mb-1" htmlFor="reg-pass">
                    Password
                  </label>
                  <input
                    id="reg-pass"
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Create a password"
                    className="w-full px-4 py-2.5 bg-surface-container-low/60 border border-surface-container-high rounded-2xl text-xs sm:text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-secondary/50 focus:bg-white transition-all placeholder:text-outline"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-on-surface mb-1" htmlFor="reg-confirm">
                    Confirm Password
                  </label>
                  <input
                    id="reg-confirm"
                    type="password"
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Confirm your password"
                    className="w-full px-4 py-2.5 bg-surface-container-low/60 border border-surface-container-high rounded-2xl text-xs sm:text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-secondary/50 focus:bg-white transition-all placeholder:text-outline"
                  />
                </div>
              </div>

              {/* Household Scope (Starts unselected) */}
              <div>
                <label className="block text-xs font-bold text-on-surface mb-1.5">
                  Household Pantry Scope
                </label>
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <button
                    type="button"
                    onClick={() => setHouseholdType('solo')}
                    className={`py-2 px-3 rounded-xl border text-center font-semibold transition-all cursor-pointer ${
                      householdType === 'solo'
                        ? 'bg-secondary-container text-on-secondary-container border-secondary shadow-2xs'
                        : 'bg-surface-container-low border-surface-container-high text-on-surface-variant hover:border-secondary/50'
                    }`}
                  >
                    🌱 Solo Chef
                  </button>
                  <button
                    type="button"
                    onClick={() => setHouseholdType('couple')}
                    className={`py-2 px-3 rounded-xl border text-center font-semibold transition-all cursor-pointer ${
                      householdType === 'couple'
                        ? 'bg-secondary-container text-on-secondary-container border-secondary shadow-2xs'
                        : 'bg-surface-container-low border-surface-container-high text-on-surface-variant hover:border-secondary/50'
                    }`}
                  >
                    🌿 Couple
                  </button>
                  <button
                    type="button"
                    onClick={() => setHouseholdType('family')}
                    className={`py-2 px-3 rounded-xl border text-center font-semibold transition-all cursor-pointer ${
                      householdType === 'family'
                        ? 'bg-secondary-container text-on-secondary-container border-secondary shadow-2xs'
                        : 'bg-surface-container-low border-surface-container-high text-on-surface-variant hover:border-secondary/50'
                    }`}
                  >
                    🍃 Family
                  </button>
                </div>
              </div>

              {/* Agreement (Starts unchecked) */}
              <div className="pt-1">
                <label className="flex items-start gap-2 cursor-pointer text-[11px] text-on-surface-variant">
                  <input
                    type="checkbox"
                    checked={agreeTerms}
                    onChange={(e) => setAgreeTerms(e.target.checked)}
                    className="w-4 h-4 mt-0.5 rounded text-secondary border-surface-container-high focus:ring-secondary cursor-pointer"
                  />
                  <span>
                    I agree to the FoodFresh AI Terms of Service and Privacy Standards.
                  </span>
                </label>
              </div>

              {/* Submit */}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 px-6 rounded-full bg-primary hover:bg-primary-container text-white font-bold text-sm shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 active:scale-98 disabled:opacity-60 cursor-pointer mt-2"
              >
                {loading ? 'Creating Account…' : 'Create My Account'}
              </button>
            </form>

            <p className="text-center text-xs text-on-surface-variant mt-5">
              Already have an account?{' '}
              <button
                type="button"
                onClick={() => navigate('/login')}
                className="font-bold text-secondary hover:underline cursor-pointer"
              >
                Sign in here
              </button>
            </p>
          </div>

          <div className="pt-2 text-center text-[11px] text-outline">
            FoodFresh AI • Intelligent Kitchen Ecology
          </div>
        </div>
      </div>
    </div>
  );
}

export default RegisterPage;
