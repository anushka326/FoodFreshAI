import React, { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth.js';
import { UserAvatar } from '../../components/common/UserAvatar.jsx';
import { Toast } from '../../components/common/Toast.jsx';

export function SettingsPage({ navigate }) {
  const { user, updateProfile, logout } = useAuth();
  const [fullName, setFullName] = useState(user?.fullName || 'Kitchen Chef');
  const [email, setEmail] = useState(user?.email || '');
  const [tempUnit, setTempUnit] = useState('C');
  const [dailyReminders, setDailyReminders] = useState(true);
  const [urgentAlerts, setUrgentAlerts] = useState(true);
  const [roadmapOnDashboard, setRoadmapOnDashboard] = useState(true);
  const [floatingBuddy, setFloatingBuddy] = useState(true);
  const [autoSaveHistory, setAutoSaveHistory] = useState(true);

  const [toastMessage, setToastMessage] = useState('');
  const [showToast, setShowToast] = useState(false);

  useEffect(() => {
    if (user) {
      if (user.fullName) setFullName(user.fullName);
      if (user.email) setEmail(user.email);
    }
  }, [user]);

  const triggerToast = (msg) => {
    setToastMessage(msg);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    await updateProfile({ fullName, email });
    triggerToast('Kitchen profile updated successfully!');
  };

  const handleSignOut = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="max-w-4xl space-y-8 pb-12 font-sans">
      <Toast message={toastMessage} visible={showToast} />

      {/* Page Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-primary tracking-tight">
          Kitchen Preferences & Settings
        </h1>
        <p className="text-xs sm:text-sm text-on-surface-variant mt-0.5">
          Configure temperature units, notification pacing, and FreshoBuddy behavior.
        </p>
      </div>

      {/* User Profile Card */}
      <div className="p-6 rounded-3xl bg-white border border-surface-container-high/70 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-4 text-center sm:text-left">
          <div className="relative">
            <UserAvatar
              src={user?.avatarUrl}
              name={fullName || 'Kitchen Chef'}
              size="xl"
            />
            <span className="absolute bottom-0 right-0 w-4 h-4 bg-secondary border-2 border-white rounded-full" />
          </div>
          <div>
            <div className="flex items-center justify-center sm:justify-start gap-2">
              <h2 className="text-lg font-extrabold text-primary">{fullName || 'Kitchen Chef'}</h2>
              <span className="px-2 py-0.5 rounded-full bg-secondary-container text-on-secondary-container text-[10px] font-bold">
                Chef Active
              </span>
            </div>
            <p className="text-xs text-on-surface-variant">{email || 'No email configured'}</p>
            <p className="text-[11px] text-secondary font-semibold mt-1">Pantry Guard Protocol Active</p>
          </div>
        </div>

        <button
          type="button"
          onClick={() => triggerToast('Avatar customization will be available when file storage is connected.')}
          className="px-4 py-2 rounded-full bg-surface-container-low hover:bg-surface-container text-primary font-bold text-xs transition-colors cursor-pointer"
        >
          Change Photo
        </button>
      </div>

      {/* Section 1: Kitchen Profile Info */}
      <form onSubmit={handleSaveProfile} className="p-6 sm:p-8 rounded-3xl bg-white border border-surface-container-high/70 shadow-sm space-y-5">
        <h2 className="text-base font-extrabold text-primary">Kitchen Profile Information</h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold text-on-surface mb-1.5" htmlFor="settings-name">
              Display Name
            </label>
            <input
              id="settings-name"
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Enter your name"
              className="w-full px-4 py-2.5 bg-surface-container-low/60 border border-surface-container-high rounded-2xl text-xs sm:text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-secondary/40 placeholder:text-outline"
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-on-surface mb-1.5" htmlFor="settings-email">
              Kitchen Email
            </label>
            <input
              id="settings-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email address"
              className="w-full px-4 py-2.5 bg-surface-container-low/60 border border-surface-container-high rounded-2xl text-xs sm:text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-secondary/40 placeholder:text-outline"
            />
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <button
            type="submit"
            className="px-6 py-2.5 rounded-full bg-primary hover:bg-primary-container text-white text-xs font-bold shadow-sm transition-all cursor-pointer"
          >
            Save Profile Changes
          </button>
        </div>
      </form>

      {/* Section 2: Temperature Units */}
      <div className="p-6 rounded-3xl bg-white border border-surface-container-high/70 shadow-sm space-y-4">
        <div>
          <h2 className="text-base font-extrabold text-primary">Storage Temperature Units</h2>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Choose how ambient countertop and crisper refrigerator temperatures are displayed.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-3 max-w-sm">
          <button
            type="button"
            onClick={() => {
              setTempUnit('C');
              triggerToast('Temperature units set to Celsius (°C)');
            }}
            className={`p-3.5 rounded-2xl border text-center font-bold text-xs transition-all cursor-pointer ${
              tempUnit === 'C'
                ? 'bg-secondary-container text-on-secondary-container border-secondary'
                : 'bg-surface-container-low text-on-surface-variant border-surface-container-high'
            }`}
          >
            Celsius (°C)
          </button>
          <button
            type="button"
            onClick={() => {
              setTempUnit('F');
              triggerToast('Temperature units set to Fahrenheit (°F)');
            }}
            className={`p-3.5 rounded-2xl border text-center font-bold text-xs transition-all cursor-pointer ${
              tempUnit === 'F'
                ? 'bg-secondary-container text-on-secondary-container border-secondary'
                : 'bg-surface-container-low text-on-surface-variant border-surface-container-high'
            }`}
          >
            Fahrenheit (°F)
          </button>
        </div>
      </div>

      {/* Section 3: Notification & Pacing */}
      <div className="p-6 rounded-3xl bg-white border border-surface-container-high/70 shadow-sm space-y-4">
        <div>
          <h2 className="text-base font-extrabold text-primary">Pantry Reminders & Notifications</h2>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Manage how FoodFresh AI alerts you to impending produce quality windows.
          </p>
        </div>

        <div className="space-y-3">
          <label className="flex items-center justify-between p-3.5 rounded-2xl bg-surface-container-low/70 border border-surface-container-high/50 cursor-pointer">
            <div>
              <span className="font-bold text-xs text-primary block">Daily 9:00 AM Counter Review</span>
              <span className="text-[11px] text-on-surface-variant">
                Brief morning nudge with your top 3 Eat First foods.
              </span>
            </div>
            <input
              type="checkbox"
              checked={dailyReminders}
              onChange={(e) => setDailyReminders(e.target.checked)}
              className="w-4 h-4 rounded text-secondary focus:ring-secondary"
            />
          </label>

          <label className="flex items-center justify-between p-3.5 rounded-2xl bg-surface-container-low/70 border border-surface-container-high/50 cursor-pointer">
            <div>
              <span className="font-bold text-xs text-primary block">Urgent 24-Hour Expiry Alert</span>
              <span className="text-[11px] text-on-surface-variant">
                Immediate notification when produce reaches its final culinary window.
              </span>
            </div>
            <input
              type="checkbox"
              checked={urgentAlerts}
              onChange={(e) => setUrgentAlerts(e.target.checked)}
              className="w-4 h-4 rounded text-secondary focus:ring-secondary"
            />
          </label>
        </div>
      </div>

      {/* Section 4: Interface & Feature Toggles */}
      <div className="p-6 rounded-3xl bg-white border border-surface-container-high/70 shadow-sm space-y-4">
        <div>
          <h2 className="text-base font-extrabold text-primary">Dashboard & Feature Preferences</h2>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Customize which interactive modules appear on your home workspace.
          </p>
        </div>

        <div className="space-y-3">
          <label className="flex items-center justify-between p-3.5 rounded-2xl bg-surface-container-low/70 border border-surface-container-high/50 cursor-pointer">
            <div>
              <span className="font-bold text-xs text-primary block">Eat First Roadmap Priority Engine</span>
              <span className="text-[11px] text-on-surface-variant">
                Display the Eat First priority section and progress tracker on the dashboard.
              </span>
            </div>
            <input
              type="checkbox"
              checked={roadmapOnDashboard}
              onChange={(e) => {
                setRoadmapOnDashboard(e.target.checked);
                triggerToast(e.target.checked ? 'Eat First Roadmap enabled on Dashboard' : 'Eat First Roadmap hidden from Dashboard');
              }}
              className="w-4 h-4 rounded text-secondary focus:ring-secondary"
            />
          </label>

          <label className="flex items-center justify-between p-3.5 rounded-2xl bg-surface-container-low/70 border border-surface-container-high/50 cursor-pointer">
            <div>
              <span className="font-bold text-xs text-primary block">FreshoBuddy Floating Widget</span>
              <span className="text-[11px] text-on-surface-variant">
                Show the bottom-right interactive companion avatar across pages.
              </span>
            </div>
            <input
              type="checkbox"
              checked={floatingBuddy}
              onChange={(e) => setFloatingBuddy(e.target.checked)}
              className="w-4 h-4 rounded text-secondary focus:ring-secondary"
            />
          </label>

          <label className="flex items-center justify-between p-3.5 rounded-2xl bg-surface-container-low/70 border border-surface-container-high/50 cursor-pointer">
            <div>
              <span className="font-bold text-xs text-primary block">Auto-Save Scans to Pantry History</span>
              <span className="text-[11px] text-on-surface-variant">
                Automatically archive new food inspections without needing manual button clicks.
              </span>
            </div>
            <input
              type="checkbox"
              checked={autoSaveHistory}
              onChange={(e) => setAutoSaveHistory(e.target.checked)}
              className="w-4 h-4 rounded text-secondary focus:ring-secondary"
            />
          </label>
        </div>
      </div>

      {/* Section 5: Account Security & Sign Out */}
      <div className="p-6 rounded-3xl bg-surface-container-low border border-surface-container-high/60 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-bold text-primary">Session Management</h2>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Sign out of this device or manage active kitchen sessions.
          </p>
        </div>

        <button
          type="button"
          onClick={handleSignOut}
          className="px-5 py-2.5 rounded-full bg-error-container hover:bg-red-200 text-error text-xs font-bold transition-colors cursor-pointer"
        >
          Sign Out of Kitchen
        </button>
      </div>
    </div>
  );
}

export default SettingsPage;
