# FoodFresh AI — Frontend

This is the organized frontend application for **FoodFresh AI** (Know. Save. Waste Less.), structured from Google Stitch exports.

## Directory Structure

```
frontend/
├── public/
│   └── icons/
│       ├── logo.svg
│       └── fresho-buddy.svg
├── src/
│   ├── assets/
│   │   ├── branding/          # FoodFresh AI brand logos & marks
│   │   ├── mascot/            # FreshoBuddy character SVG & asset descriptors
│   │   ├── food/              # Real produce visual assets (apples, tomatoes, bananas, bowl)
│   │   └── illustrations/     # Botanical and produce motifs
│   ├── components/
│   │   ├── common/            # Shared primitives (Toast, Badges, etc.)
│   │   ├── layout/            # Navbar, Sidebar, AppLayout
│   │   └── fresho-buddy/      # Floating companion widget & mini chat
│   ├── hooks/
│   │   ├── useAuth.js         # Authentication state hook
│   │   └── useFoodFresh.js    # Pantry logs & Eat First roadmap hook
│   ├── pages/
│   │   ├── LandingPage/       # Splash animation & high-converting landing presentation
│   │   ├── LoginPage/         # Chef authentication screen with Stitch form states
│   │   ├── RegisterPage/      # Household pantry onboarding
│   │   ├── DashboardPage/     # Kitchen overview with Eat First Roadmap & recent analyses
│   │   ├── AnalyzeFoodPage/   # Produce photo scanner, context controls, & results
│   │   ├── AnalysisHistoryPage/ # Searchable produce log & slide-out inspection drawer
│   │   ├── SettingsPage/      # Household preferences & temperature units
│   │   └── FreshoBuddyPage/   # Dedicated conversational AI sous-chef studio
│   ├── services/
│   │   ├── authService.js     # Prepared interfaces for future FastAPI /api/v1/auth
│   │   ├── analysisService.js # Prepared interfaces for future FastAPI /api/v1/analyze
│   │   ├── historyService.js  # Prepared interfaces for future FastAPI /api/v1/history
│   │   ├── roadmapService.js  # Prepared interfaces for future FastAPI /api/v1/roadmap
│   │   └── freshoBuddyService.js # Prepared interfaces for future FastAPI /api/v1/fresho-buddy
│   ├── utils/
│   │   ├── foodUtils.js       # Status badge styling and priority rank mappings
│   │   └── formatters.js      # Date and metric formatters
│   ├── App.jsx                # Client-side router & screen coordinator
│   └── index.css              # Stitch design system color palette & Plus Jakarta Sans
├── package.json
└── README.md
```

## Running the Frontend

```bash
npm install
npm run dev
```

The application runs on Vite with Tailwind CSS v4 and Plus Jakarta Sans typography.

## Backend Independence

All components consume API interfaces located in `src/services/`. These services currently provide mock client-side state so that the user interface operates smoothly and can be plugged directly into FastAPI endpoints in future milestones without component redesign.
