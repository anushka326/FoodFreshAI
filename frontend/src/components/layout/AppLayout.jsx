import React, { useState } from 'react';
import { Navbar } from './Navbar.jsx';
import { Sidebar } from './Sidebar.jsx';
import { FreshoBuddyFloatingWidget } from '../fresho-buddy/FreshoBuddyFloatingWidget.jsx';

export function AppLayout({ children, currentRoute, navigate }) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-surface flex flex-col font-sans text-on-surface">
      {/* Fixed Sidebar */}
      <Sidebar
        currentRoute={currentRoute}
        navigate={navigate}
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col lg:pl-72 transition-all duration-300">
        {/* Top Navbar */}
        <Navbar
          onMenuToggle={() => setIsSidebarOpen(!isSidebarOpen)}
          currentRoute={currentRoute}
          navigate={navigate}
        />

        {/* Dynamic Page Content */}
        <main className="flex-1 pt-24 px-4 sm:px-8 lg:px-12 max-w-7xl w-full mx-auto">
          {children}
        </main>
      </div>

      {/* Floating FreshoBuddy Assistant Widget (bottom-right on authenticated pages except full FreshoBuddy studio) */}
      {currentRoute !== '/fresho-buddy' && (
        <FreshoBuddyFloatingWidget navigate={navigate} currentRoute={currentRoute} />
      )}
    </div>
  );
}

export default AppLayout;
