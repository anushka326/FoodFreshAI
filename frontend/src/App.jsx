import React, { useState, useEffect } from 'react';
import { LandingPage } from './pages/LandingPage/LandingPage.jsx';
import { LoginPage } from './pages/LoginPage/LoginPage.jsx';
import { RegisterPage } from './pages/RegisterPage/RegisterPage.jsx';
import { DashboardPage } from './pages/DashboardPage/DashboardPage.jsx';
import { AnalyzeFoodPage } from './pages/AnalyzeFoodPage/AnalyzeFoodPage.jsx';
import { AnalysisHistoryPage } from './pages/AnalysisHistoryPage/AnalysisHistoryPage.jsx';
import { SettingsPage } from './pages/SettingsPage/SettingsPage.jsx';
import { FreshoBuddyPage } from './pages/FreshoBuddyPage/FreshoBuddyPage.jsx';
import { RecipeRecommendationsPage } from './pages/RecipeRecommendationsPage/RecipeRecommendationsPage.jsx';
import { ImpactAnalyticsPage } from './pages/ImpactAnalyticsPage/ImpactAnalyticsPage.jsx';
import { PackagedFoodScannerPage } from './pages/PackagedFoodScannerPage/PackagedFoodScannerPage.jsx';
import { AppLayout } from './components/layout/AppLayout.jsx';
import { authService } from './services/authService.js';
import { OfflineStatusBanner } from './components/common/OfflineStatusBanner.jsx';
import { PwaInstallPrompt } from './components/common/PwaInstallPrompt.jsx';

const PROTECTED_ROUTES = ['/dashboard', '/analyze', '/packaged-food', '/history', '/settings', '/fresho-buddy', '/recipes', '/analytics'];

export function App() {
  // Support both window.location.pathname / hash or clean state router with auth guard
  const getInitialRoute = () => {
    const hash = window.location.hash.replace('#', '');
    const path = hash || window.location.pathname;
    if (['/login', '/register', ...PROTECTED_ROUTES].includes(path)) {
      if (PROTECTED_ROUTES.includes(path) && !authService.isAuthenticated()) {
        sessionStorage.setItem('foodfresh_redirect_after_login', path);
        return '/login';
      }
      return path;
    }
    return '/';
  };

  const [currentRoute, setCurrentRoute] = useState(getInitialRoute);

  const navigate = (path) => {
    if (PROTECTED_ROUTES.includes(path) && !authService.isAuthenticated()) {
      sessionStorage.setItem('foodfresh_redirect_after_login', path);
      sessionStorage.setItem(
        'foodfresh_auth_notice',
        path === '/analyze'
          ? 'Authentication required: Sign in with your credentials to start analyzing food.'
          : 'Authentication required: Please sign in with your credentials to access kitchen features.'
      );
      setCurrentRoute('/login');
      window.location.hash = '/login';
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }
    setCurrentRoute(path);
    window.location.hash = path;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  useEffect(() => {
    // Validate session with backend on initial load
    authService.validateSessionAsync().then((isValid) => {
      if (!isValid && PROTECTED_ROUTES.includes(currentRoute)) {
        sessionStorage.setItem('foodfresh_redirect_after_login', currentRoute);
        sessionStorage.setItem(
          'foodfresh_auth_notice',
          'Your kitchen session has expired or requires authentication. Please sign in.'
        );
        setCurrentRoute('/login');
        window.location.hash = '/login';
      }
    });

    const handleAuthStateChange = (e) => {
      if (!e.detail?.authenticated && PROTECTED_ROUTES.includes(currentRoute)) {
        setCurrentRoute('/login');
        window.location.hash = '/login';
      }
    };

    const handleHashChange = () => {
      const hash = window.location.hash.replace('#', '') || '/';
      if (PROTECTED_ROUTES.includes(hash) && !authService.isAuthenticated()) {
        sessionStorage.setItem('foodfresh_redirect_after_login', hash);
        sessionStorage.setItem(
          'foodfresh_auth_notice',
          'Please sign in with your credentials to access kitchen features.'
        );
        setCurrentRoute('/login');
        window.location.hash = '/login';
        return;
      }
      setCurrentRoute(hash);
    };

    window.addEventListener('hashchange', handleHashChange);
    window.addEventListener('foodfresh_auth_state_changed', handleAuthStateChange);
    return () => {
      window.removeEventListener('hashchange', handleHashChange);
      window.removeEventListener('foodfresh_auth_state_changed', handleAuthStateChange);
    };
  }, [currentRoute]);

  // Determine view rendering
  const renderView = () => {
    // Runtime safety guard: protect in-app routes from unauthenticated access
    if (PROTECTED_ROUTES.includes(currentRoute) && !authService.isAuthenticated()) {
      return <LoginPage navigate={navigate} />;
    }

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
      case '/packaged-food':
        return (
          <AppLayout currentRoute={currentRoute} navigate={navigate}>
            <PackagedFoodScannerPage navigate={navigate} />
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
      case '/recipes':
        return (
          <AppLayout currentRoute={currentRoute} navigate={navigate}>
            <RecipeRecommendationsPage navigate={navigate} />
          </AppLayout>
        );
      case '/analytics':
        return (
          <AppLayout currentRoute={currentRoute} navigate={navigate}>
            <ImpactAnalyticsPage navigate={navigate} />
          </AppLayout>
        );
      case '/':
      default:
        return <LandingPage navigate={navigate} />;
    }
  };

  return (
    <div className="foodfresh-app-root">
      {renderView()}
      <OfflineStatusBanner />
      <PwaInstallPrompt variant="banner" />
    </div>
  );
}

export default App;
