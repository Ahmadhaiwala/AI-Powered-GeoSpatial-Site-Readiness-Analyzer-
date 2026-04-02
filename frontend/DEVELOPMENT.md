# Development Guide - GeoSpatial Site Readiness Analyzer

## Overview

This document provides detailed guidance for developers working on the GeoSpatial Site Readiness Analyzer application.

## Development Environment Setup

### Prerequisites
- Node.js 18.0 or higher
- pnpm 8.0 or higher (recommended over npm/yarn for performance)
- Git

### Initial Setup

```bash
# Clone the repository
git clone <repository-url>
cd geospatial-site-readiness-analyzer

# Install dependencies
pnpm install

# Start development server
pnpm dev
```

## Development Workflow

### Code Structure

The application follows a modular component architecture:

```
src/
├── components/          # React components (UI and feature)
├── hooks/              # Custom React hooks
├── utils/              # Utility functions
├── store.ts            # Global state with Zustand
├── App.tsx             # Root component
├── main.tsx            # Entry point
└── index.css           # Global styles
```

### Component Guidelines

#### Creating New Components

1. Create a new file in `src/components/` with PascalCase naming
2. Use TypeScript for type safety
3. Import only necessary dependencies
4. Use UnoCSS class names (Tailwind-compatible)
5. Export as named export

Example:
```tsx
import { useState } from 'react'
import { ChevronDown } from 'lucide-react'

interface MyComponentProps {
  title: string
  onClose: () => void
}

export function MyComponent({ title, onClose }: MyComponentProps) {
  const [isOpen, setIsOpen] = useState(false)
  
  return (
    <div className="p-4 rounded-lg bg-slate-800">
      <button onClick={() => setIsOpen(!isOpen)}>
        {title}
        <ChevronDown size={20} />
      </button>
    </div>
  )
}
```

### State Management with Zustand

Global state is managed through `src/store.ts`. To use store state:

```tsx
import { useMapStore } from '../store'

export function MyComponent() {
  const selectedLocation = useMapStore((state) => state.selectedLocation)
  const selectLocation = useMapStore((state) => state.selectLocation)
  
  return (
    <button onClick={() => selectLocation(myLocation)}>
      Select Location
    </button>
  )
}
```

#### Adding New Store State

Edit `src/store.ts` to add new state and actions:

```typescript
export interface MapState {
  // ... existing state
  newProperty: any
  updateNewProperty: (value: any) => void
}

export const useMapStore = create<MapState>((set) => ({
  // ... existing state
  newProperty: null,
  updateNewProperty: (value) => set({ newProperty: value }),
}))
```

### Styling with UnoCSS

This project uses UnoCSS with Tailwind CSS preset. All styling follows Tailwind conventions:

#### Common Utilities

```tsx
// Spacing
className="p-4 m-2 gap-3"

// Colors
className="bg-slate-800 text-slate-300 border-slate-700"

// Layout
className="flex items-center justify-between"
className="grid grid-cols-2 gap-4"

// Responsive
className="w-full md:w-1/2 lg:w-1/3"

// Animations
className="transition-all duration-300 hover:bg-slate-700"
```

#### Color Palette

- **Slate**: Neutral backgrounds and text (`slate-50` to `slate-900`)
- **Emerald**: Success and primary actions (`emerald-400`, `emerald-600`)
- **Amber**: Warnings and cautions (`amber-400`, `amber-600`)
- **Red**: Errors and high priority (`red-400`, `red-600`)

### Mapping Integration

The application uses Leaflet for mapping through React-Leaflet wrapper:

```tsx
import L from 'leaflet'
import { useMapStore } from '../store'

// Access map reference through useRef
const mapRef = useRef<L.Map | null>(null)

// Initialize map
mapRef.current = L.map('map-element').setView([lat, lng], zoom)

// Add tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors',
  maxZoom: 19,
}).addTo(mapRef.current)
```

### Scoring Algorithm

The scoring algorithm is in `src/utils/scoreGenerator.ts`. To modify scoring logic:

```typescript
export function generateScore(businessType: string): SiteScore {
  // Define base factors per business type
  const baseFactors = {
    retail: { /* factors */ },
    // ... other types
  }
  
  // Add randomization for variance
  // Calculate weighted average
  // Return SiteScore object
}
```

## Build and Deployment

### Development Build

```bash
pnpm dev
```

Starts Vite dev server with HMR on `http://localhost:5173`

### Production Build

```bash
pnpm build
```

Creates optimized bundle in `dist/` directory:
- ~375KB gzipped JavaScript
- ~2.7KB gzipped CSS
- Fully tree-shaken and optimized

### Preview Build

```bash
pnpm preview
```

Serves the production build locally for testing.

## Git Workflow

### Branch Naming
- Feature: `feature/description`
- Bug fix: `fix/description`
- Improvement: `improve/description`

### Commit Messages
Use clear, descriptive commit messages:
```
feat: add location export functionality
fix: correct factor calculation weights
refactor: simplify score card component
```

### Pull Requests
- Reference issues when applicable
- Include description of changes
- Request review before merging

## Testing

Currently, the project doesn't have automated tests. To add tests:

1. Install testing dependencies:
```bash
pnpm add -D vitest @testing-library/react @testing-library/user-event
```

2. Create `vitest.config.ts` for configuration

3. Write tests in `__tests__` directories alongside components

Example test:
```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ScoreCard } from './ScoreCard'

describe('ScoreCard', () => {
  it('displays score correctly', () => {
    const location = { /* mock data */ }
    render(<ScoreCard location={location} />)
    expect(screen.getByText(/85/)).toBeInTheDocument()
  })
})
```

## Performance Optimization

### Code Splitting
Vite automatically code splits at build time. For runtime code splitting:

```tsx
const HeavyComponent = lazy(() => import('./HeavyComponent'))

export function App() {
  return (
    <Suspense fallback={<Spinner />}>
      <HeavyComponent />
    </Suspense>
  )
}
```

### Memoization
Use `memo` for expensive components:

```tsx
import { memo } from 'react'

const FactorBreakdown = memo(function FactorBreakdown({ factors }) {
  return /* component */
})
```

### Bundle Analysis
Check bundle size:

```bash
pnpm build --analyze
```

## Debugging

### Browser DevTools
- Use React DevTools for component inspection
- Check Network tab for API calls
- Console logs with `[v0]` prefix for clarity

### VSCode Debug Configuration
Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "chrome",
      "request": "launch",
      "name": "Launch Chrome",
      "url": "http://localhost:5173",
      "webRoot": "${workspaceFolder}/src"
    }
  ]
}
```

## Common Tasks

### Adding a New Business Type

1. Update `businessTypes` array in `BusinessTypeSelector.tsx`
2. Add scoring factors in `scoreGenerator.ts`
3. Add recommendations in `RecommendationsList.tsx`
4. Test scoring across the app

### Modifying Map Behavior

Edit `MapContainer.tsx`:
- Change tile provider in `L.tileLayer()`
- Adjust click handling in `map.on('click', ...)`
- Modify marker styling in `L.marker()` options

### Updating Explanations

Edit `ExplanationPanel.tsx`:
- Update `explanations` object for business types
- Modify insights structure and layout
- Add new explanation sections

## Troubleshooting

### Dev Server Not Starting
```bash
# Kill existing process on port 5173
lsof -i :5173 | grep LISTEN | awk '{print $2}' | xargs kill -9
# Restart
pnpm dev
```

### Module Not Found Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules
pnpm install
```

### Build Errors
```bash
# Clean build artifacts and rebuild
rm -rf dist
pnpm build
```

### Leaflet Marker Icons Missing
- Ensure Leaflet CSS is loaded (handled in `index.html`)
- Check CDN links are accessible
- Verify marker icon configuration in `MapContainer.tsx`

## Resources

- [Vite Documentation](https://vitejs.dev/)
- [React Documentation](https://react.dev/)
- [UnoCSS Documentation](https://unocss.dev/)
- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [Leaflet Documentation](https://leafletjs.com/)
- [Lucide Icons](https://lucide.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/)

## Contributing

1. Create a feature branch
2. Make changes following guidelines above
3. Test thoroughly in development
4. Submit pull request with description
5. Address review feedback
6. Merge when approved

## Questions?

Refer to the README.md for user documentation or ask in the development team channels.
