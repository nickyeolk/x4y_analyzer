# Startup Analyzer Frontend

Modern React frontend for the Startup Analyzer AI-powered business idea analysis platform.

## Features

- 🚀 **Real-time SSE Streaming** - Watch agents work in real-time
- 📊 **Live Progress Display** - See each agent as they analyze your idea
- 💎 **Beautiful UI** - Clean, responsive design with smooth animations
- 📈 **Metrics Dashboard** - Viability score, cost, duration, and token usage
- 🎯 **Comprehensive Results** - Detailed insights from all four agents
- 🔄 **Loop Indicators** - Visual feedback when Skeptic triggers quality loops

## Tech Stack

- **React 18** - Modern React with hooks
- **Vite** - Fast build tool and dev server
- **Vanilla CSS** - Clean, maintainable styles with CSS variables
- **EventSource/Fetch API** - Native browser SSE streaming

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── AnalysisForm.jsx         # Input form for "X for Y" ideas
│   │   ├── ProgressDisplay.jsx      # Real-time agent progress
│   │   ├── MetricsDashboard.jsx     # Metrics and viability score
│   │   └── ResultsDisplay.jsx       # Complete analysis results
│   ├── hooks/
│   │   └── useSSE.js                # Custom SSE streaming hook
│   ├── styles/
│   │   └── index.css                # Global styles and theme
│   ├── App.jsx                      # Main application component
│   └── main.jsx                     # Application entry point
├── index.html                       # HTML template
├── vite.config.js                   # Vite configuration
└── package.json                     # Dependencies and scripts
```

## Getting Started

### Prerequisites

- Node.js 18+ or npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### Development

```bash
# Start development server
npm run dev
```

The application will be available at `http://localhost:3000`

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Usage

1. **Enter Your Idea**
   - Fill in the "X Brand" (e.g., Uber, Netflix, Airbnb)
   - Fill in the "Y Market" (e.g., Dog Walkers, Fitness Classes)
   - Optionally add a description
   - Or click an example to load pre-filled data

2. **Watch the Analysis**
   - See the progress bar update as each agent works
   - View loop indicators if Skeptic requests deeper analysis
   - Real-time updates via SSE streaming

3. **Review Results**
   - Viability score (0-10)
   - Detailed insights from each agent
   - Metrics: duration, cost, token usage, iterations
   - Complete GTM strategy

## API Integration

The frontend connects to the backend API via:

- **Endpoint**: `POST /api/analyze/stream`
- **Method**: Server-Sent Events (SSE)
- **Proxy**: Configured in `vite.config.js` for development

### SSE Event Flow

```
analysis_started
  ↓
agent_started (analyst)
agent_completed (analyst)
  ↓
agent_started (researcher)
agent_completed (researcher)
  ↓
agent_started (skeptic)
agent_completed (skeptic)
  ↓
[loop_triggered] (if quality improvement needed)
  ↓
agent_started (strategist)
agent_completed (strategist)
  ↓
analysis_completed
  ↓
result (complete JSON)
```

## Components

### AnalysisForm

Input form with validation and example ideas.

**Props:**
- `onSubmit(request)` - Called when form is submitted
- `isLoading` - Disables form during analysis

### ProgressDisplay

Real-time progress indicator for all agents.

**Props:**
- `events` - Array of SSE events
- `isConnected` - Whether SSE connection is active

### MetricsDashboard

Displays viability score and analysis metrics.

**Props:**
- `result` - Complete analysis result object

### ResultsDisplay

Shows detailed results from all four agents.

**Props:**
- `result` - Complete analysis result object

### useSSE Hook

Custom hook for SSE streaming.

**Parameters:**
- `url` - SSE endpoint URL
- `body` - Request body to POST
- `shouldConnect` - Whether to initiate connection

**Returns:**
- `events` - Array of received events
- `isConnected` - Connection status
- `error` - Error object if any
- `result` - Final result when complete
- `disconnect()` - Function to close connection

## Styling

The application uses CSS variables for theming:

```css
:root {
  --primary-color: #3b82f6;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --error-color: #ef4444;
  /* ... more variables */
}
```

Responsive breakpoints:
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

## Features in Detail

### Real-time Streaming

Uses the custom `useSSE` hook to consume Server-Sent Events:

```jsx
const { events, isConnected, result } = useSSE(
  '/api/analyze/stream',
  { x_brand: 'Uber', y_market: 'Dog Walkers' },
  true
);
```

### Agent Progress

Visual indicators for each agent:
- 🔍 Brand Analyst - Pending/Active/Completed
- 📊 Market Researcher - Pending/Active/Completed
- 🤔 Skeptic - Pending/Active/Completed
- 🎯 Strategist - Pending/Active/Completed

### Loop Detection

When the Skeptic triggers a quality loop:
- Yellow warning banner appears
- Shows iteration count
- Displays loop reason
- Progress resets to Analyst

### Viability Score

Large circular display showing:
- Score from 0-10
- Color gradient (purple/blue)
- Interpretation (Highly Viable, Viable, Moderate, Low)

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Any browser with EventSource/Fetch API support

## Development Tips

### Hot Module Replacement

Vite provides instant HMR - changes appear immediately without refresh.

### API Proxy

Development proxy routes `/api/*` requests to `http://localhost:8000`:

```js
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

### Error Handling

The app handles various error states:
- API connection errors
- SSE streaming errors
- Invalid responses
- Timeout scenarios

## Deployment

### Build Outputs

```bash
npm run build
```

Creates optimized production files in `dist/`:
- Minified JavaScript
- Optimized CSS
- Static assets
- HTML entry point

### Environment Variables

For production, configure:
- `VITE_API_URL` - Backend API URL (if different from proxy)

### Serve Static Files

The built files can be served by:
- FastAPI (serve from `/static`)
- Nginx
- Caddy
- Railway
- Vercel
- Netlify

## Performance

- **Initial Load**: < 50KB JavaScript (gzipped)
- **Lazy Loading**: Components loaded on demand
- **Code Splitting**: Automatic with Vite
- **CSS**: Single optimized stylesheet
- **Assets**: Minified and fingerprinted

## Future Enhancements

- [ ] Dark mode toggle
- [ ] Result export (PDF, JSON)
- [ ] Share analysis link
- [ ] Analysis history
- [ ] Comparison mode (multiple ideas)
- [ ] LangSmith trace viewer embed
- [ ] Advanced filters
- [ ] Mobile app version

## Troubleshooting

### SSE Not Connecting

1. Ensure backend is running: `http://localhost:8000/health`
2. Check browser console for errors
3. Verify proxy configuration in `vite.config.js`
4. Try disabling browser extensions

### Events Not Showing

1. Check Network tab for SSE stream
2. Verify events are being sent by backend
3. Check browser console for parsing errors
4. Ensure backend CORS is configured

### Slow Performance

1. Check backend response time
2. Monitor network requests in DevTools
3. Verify no memory leaks in React DevTools
4. Test with production build (`npm run build`)

## Contributing

When adding new features:

1. Keep components small and focused
2. Use the existing CSS variable system
3. Follow the established naming conventions
4. Add PropTypes or TypeScript types
5. Test SSE streaming thoroughly
6. Ensure mobile responsiveness

## License

Part of the Startup Analyzer project.

---

**Built with ❤️ using React + Vite**
