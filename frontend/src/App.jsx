import React, { useState, useEffect } from 'react';
import { LandingPage } from './pages/LandingPage/LandingPage.jsx';
import { LoginPage } from './pages/LoginPage/LoginPage.jsx';
import { RegisterPage } from './pages/RegisterPage/RegisterPage.jsx';
import { DashboardPage } from './pages/DashboardPage/DashboardPage.jsx';
import { AnalyzeFoodPage } from './pages/AnalyzeFoodPage/AnalyzeFoodPage.jsx';
import { AnalysisHistoryPage } from './pages/AnalysisHistoryPage/AnalysisHistoryPage.jsx';
import { SettingsPage } from './pages/SettingsPage/SettingsPage.jsx';
import { FreshoBuddyPage } from './pages/FreshoBuddyPage/FreshoBuddyPage.jsx';
import { AppLayout } from './components/layout/AppLayout.jsx';

export function App() {
  // Support both window.location.pathname / hash or clean state router
  const getInitialRoute = () => {
    const hash = window.location.hash.replace('#', '');
    if (hash) return hash;
    const path = window.location.pathname;
    if (['/login', '/register', '/dashboard', '/analyze', '/history', '/settings', '/fresho-buddy'].includes(path)) {
      return path;
    }
    return '/';
  };

  const [currentRoute, setCurrentRoute] = useState(getInitialRoute);

  const navigate = (path) => {
    setCurrentRoute(path);
    window.location.hash = path;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.replace('#', '') || '/';
      setCurrentRoute(hash);
    };
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  // Determine view rendering
  const renderView = () => {
    switch (currentRoute) {
      case '/login':
        return <LoginPage navigate={navigate} />;
      case '/register':
        return <RegisterPage navigate={navigate} />;
      case '/dashboard':
        return (
          <AppLayout currentRoute={currentRoute} navigate={navigate}>
            <DashboardPage navigate={navigate} />
          </AppLayout>
        );
      case '/analyze':
        return (
          <AppLayout currentRoute={currentRoute} navigate={navigate}>
            <AnalyzeFoodPage navigate={navigate} />
          </AppLayout>
        );
      case '/history':
        return (
          <AppLayout currentRoute={currentRoute} navigate={navigate}>
            <AnalysisHistoryPage navigate={navigate} />
          </AppLayout>
        );
      case '/settings':
        return (
          <AppLayout currentRoute={currentRoute} navigate={navigate}>
            <SettingsPage navigate={navigate} />
          </AppLayout>
        );
      case '/fresho-buddy':
        return (
          <AppLayout currentRoute={currentRoute} navigate={navigate}>
            <FreshoBuddyPage navigate={navigate} />
          </AppLayout>
        );
      case '/':
      default:
        return <LandingPage navigate={navigate} />;
    }
  };

  return <div className="foodfresh-app-root">{renderView()}</div>;
}

export default App;
