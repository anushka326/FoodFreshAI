# Stitch Export Reference Documentation

This directory preserves the original Google Stitch exports, comparative screen analyses, and design artifacts.

## Identified Screen Variations & States

### 1. Landing Page Variations (`/stitch-reference/landing-page-alternative/`)
- **Version 1 (Animated Entrance Overlay)**:
  - Features an introductory splash overlay with animated pulsing logo, radiating ripples, progress indicator, and "Skip" button.
  - Automatically transitions to the main landing page after 1.45 seconds or on user click.
  - Includes full responsive landing content (Hero, Everyday Dilemma Lifecycle, Core Features with Eat First preview, How It Works 4-step guide, Live Experience Gala Apple analysis card, Social Impact progression strip, Coming Soon features, and Did You Know educational facts).
- **Version 2 (Standard Immediate Landing Page)**:
  - Displays the full landing page directly without the intro splash overlay.
- **Synthesis in Frontend**:
  - In `LandingPage/LandingPage.jsx`, the entrance splash overlay is preserved as an optional toggleable state (accessible via user replay in the top bar brand mark or initial load), ensuring both design intents are seamlessly available without code loss.

### 2. Dashboard Variations (`/stitch-reference/dashboard-page-alternative/`)
- **Version 1 (Core Dashboard)**:
  - Features Good Morning greeting, Hero CTA card ("What's on your counter today?"), Quick Actions (Analyze Food, Compare Foods, View History), and Recent Analyses with state switchers (Data, Empty, Loading, Error).
- **Version 2 (Advanced Dashboard with Eat First Roadmap)**:
  - Builds on Version 1 by incorporating the dedicated **Eat First Roadmap 🥇 (Priority Engine)** section.
  - Includes progress tracking ("1 of 4 foods taken care of"), active priority cards (Ripe Vine Tomato [Eat First], Cavendish Banana [Eat Next], Haas Avocado [Can Wait]), interactive "Mark as Eaten" transitions, completed drawer with undo capability, and empty state fallback.
- **Synthesis in Frontend**:
  - The Eat First Roadmap is a direct functional superset of the dashboard. It is preserved and integrated into `DashboardPage/DashboardPage.jsx`, while the Settings page features an interactive toggle to enable/disable the Eat First Roadmap on the dashboard.

### 3. Preserved Screen Exports
- **LoginPage**: Split-card layout with fresh produce background, brand pillars, password visibility toggle, and interactive form state switchers (Normal, Error).
- **RegisterPage**: Split-card layout with onboarding feature cards, full registration fields, terms agreement, and interactive form feedback states.
- **AnalyzeFoodPage**: Deep food analysis studio supporting Single Food Item vs. Multi-Food comparison, photo upload dropzone with live preview, pantry context settings (storage location, days in kitchen, ambient temperature), loading state with 3-step scanning sequence, comprehensive single-item inspection results (score 92/100, 3-4 days remaining, snacking & storage guidance), multi-item priority ranking (Vine Tomato #1, Banana #2, Apple #3), and unrecognized photo guidance.
- **AnalysisHistoryPage**: Pantry produce log with search filter, freshness status chips (All, Fresh, Semi-Fresh, Needs Attention), metric overview cards, item table, slide-out detailed inspection drawer, delete interactions, and empty/loading states.
- **SettingsPage**: Preferences management including Profile details, temperature units (°C vs °F), notification toggles, Eat First Roadmap preference toggle, FreshoBuddy floating widget toggle, password management accordion, and account deletion confirmation modals.
- **FreshoBuddyPage**: Dedicated AI food companion interface featuring chat stream with conversational intelligence, instant discover cards, quick topic pills, pantry overview eco-longevity ring (92%), produce ethylene chemistry chart, and culinary pro-tips.
