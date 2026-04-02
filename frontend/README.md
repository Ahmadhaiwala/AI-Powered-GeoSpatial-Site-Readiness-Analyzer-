# GeoSpatial Site Readiness Analyzer

An AI-powered geospatial analysis platform built with Vite, React, and UnoCSS. Evaluate business site potential with comprehensive scoring across accessibility, infrastructure, demographics, competition, regulations, and logistics factors.

## Features

- **Interactive Map**: Click anywhere on the map to evaluate site readiness
- **Dynamic Scoring**: AI-powered scoring system (0-100) with 6-factor breakdown
- **Business Types**: Retail, Food Service, Café, Office, and Industrial evaluations
- **Smart Explanations**: AI-generated insights explaining each location's score
- **Action Items**: Prioritized recommendations based on business type
- **Real-time Analysis**: Instant score generation with factor visualization
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Tech Stack

- **Frontend**: React 19 with TypeScript
- **Styling**: UnoCSS with comprehensive Tailwind compatibility
- **Mapping**: Leaflet with React-Leaflet for interactive geospatial visualization
- **State Management**: Zustand for lightweight global state
- **Build Tool**: Vite for fast development and optimized builds
- **UI Components**: Lucide React for icons

## Getting Started

### Prerequisites
- Node.js 18+ 
- pnpm package manager

### Installation

```bash
# Install dependencies
pnpm install

# Start development server
pnpm dev

# Build for production
pnpm build

# Preview production build
pnpm preview
```

The application will be available at `http://localhost:5173`

## Usage

1. **Select Business Type**: Choose from Retail, Food Service, Café, Office, or Industrial
2. **Click on Map**: Click any location on the map to evaluate it
3. **View Scores**: See real-time scores and factor breakdown
4. **Read Insights**: Toggle "Explain Result" to see AI-generated analysis
5. **Get Recommendations**: Toggle "Recommendations" for actionable items
6. **Compare Locations**: Add multiple locations and compare their scores

## Project Structure

```
src/
├── components/          # React components
│   ├── Header.tsx      # App header
│   ├── MapContainer.tsx # Leaflet map integration
│   ├── Sidebar.tsx     # Main analysis sidebar
│   ├── ScoreCard.tsx   # Score display component
│   ├── FactorBreakdown.tsx # Factor visualization
│   ├── BusinessTypeSelector.tsx # Business type picker
│   ├── ControlPanel.tsx # Action buttons
│   ├── ExplanationPanel.tsx # AI insights
│   └── RecommendationsList.tsx # Action items
├── store.ts            # Zustand state management
├── App.tsx            # Root component
├── main.tsx           # Entry point
├── index.css          # Global styles
└── utils/
    └── scoreGenerator.ts # Scoring algorithm

Configuration Files:
- vite.config.ts       # Vite configuration
- uno.config.ts        # UnoCSS configuration
- tsconfig.json        # TypeScript configuration
- index.html           # HTML template
```

## Scoring Algorithm

The scoring system evaluates 6 key factors:
- **Accessibility** (20%): Location accessibility and foot traffic
- **Infrastructure** (18%): Available utilities and systems
- **Demographics** (18%): Population characteristics and spending power
- **Competition** (16%): Market saturation and competitor density
- **Regulations** (15%): Legal and compliance requirements
- **Logistics** (13%): Supply chain and delivery capabilities

Each factor is scored 0-100, with business-type-specific weighting and randomized variance to simulate real-world analysis variation.

## Styling with UnoCSS

The application uses UnoCSS with Tailwind CSS preset compatibility. Key color palette:
- **Primary**: Emerald (success indicators)
- **Warning**: Amber (caution items)
- **Danger**: Red (high-priority warnings)
- **Neutral**: Slate (backgrounds and text)

All utilities follow Tailwind class naming conventions for familiarity and consistency.

## Browser Support

- Chrome/Chromium (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance

- **Build Size**: ~375KB gzipped JavaScript
- **CSS**: ~2.7KB gzipped
- **Development**: Hot Module Replacement (HMR) enabled for instant updates

## Future Enhancements

- Integration with real geospatial APIs (OpenStreetMap, elevation data)
- Machine learning model integration for actual site scoring
- User authentication and saved location history
- Export reports in PDF/CSV formats
- Real-time collaboration features
- Advanced filtering and search capabilities

## License

MIT

## Contact & Support

For issues, questions, or feature requests, please refer to the documentation or submit an issue.
