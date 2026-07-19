# AI Storytelling Workspace - Web UI

Angular v22 web application for the AI Storytelling Workspace platform.

## Technology Stack

- **Framework**: Angular v22 (standalone components)
- **UI Library**: Angular Material
- **State Management**: RxJS + Services
- **HTTP Client**: Angular HttpClient
- **WebSocket**: Native WebSocket with RxJS
- **Styling**: CSS + Material theming

## Project Structure

```
src/
├── app/
│   ├── core/
│   │   └── services/
│   │       ├── api.service.ts       # HTTP API client
│   │       └── websocket.service.ts # WebSocket client
│   ├── home/
│   │   └── home.component.ts        # Home page
│   ├── app.ts                       # Root component
│   ├── app.html                     # Root template
│   ├── app.css                      # Root styles
│   ├── app.config.ts                # App configuration
│   └── app.routes.ts                # Route definitions
├── environments/
│   ├── environment.ts               # Development config
│   └── environment.prod.ts          # Production config
└── styles.css                       # Global styles
```

## Development

### Prerequisites

- Node.js 18+ and npm
- Angular CLI 22

### Install Dependencies

```bash
npm install
```

### Development Server

```bash
npm start
```

Navigate to `http://localhost:4200/`. The application will automatically reload if you change any of the source files.

### Build

```bash
npm run build
```

Build artifacts will be stored in the `dist/` directory.

### Running Tests

```bash
npm test
```

## API Configuration

The application connects to the FastAPI backend:

- **Development**: `http://localhost:8000/api`
- **Production**: `/api` (relative to current host)

WebSocket connections:

- **Development**: `ws://localhost:8000`
- **Production**: `ws://<current-host>`

## Features

### Implemented (Task 16)

- ✅ Angular v22 with standalone components
- ✅ Angular Material UI library
- ✅ Core services (API, WebSocket)
- ✅ Environment configuration
- ✅ Basic app structure with Material toolbar
- ✅ Home page component

### Planned (Tasks 17-21)

- [ ] Project Management UI (CRUD operations)
- [ ] Workflow Execution UI (real-time monitoring)
- [ ] Checkpoint Editing UI (approval/rejection)
- [ ] Image Gallery UI (display generated images)
- [ ] Story Bible Visualization UI (interactive viz)

## Material Theme

The application uses Angular Material's pre-built Indigo-Pink theme. To customize:

1. Edit `src/styles.css`
2. Import a different pre-built theme or create a custom theme

## Next Steps

See `../tasks/phase-4-angular-ui-plan.md` for detailed implementation plans for Tasks 17-21.