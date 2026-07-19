# Phase 4: Angular Web UI Implementation Plan

## Overview

Build a production-ready Angular v22 web application with TypeScript, Angular Material, and RxJS for state management. The UI will provide real-time workflow monitoring, project management, checkpoint editing, and Story Bible visualization.

## Technology Stack

- **Framework**: Angular v22 (standalone components)
- **Language**: TypeScript 5.x
- **UI Library**: Angular Material 22
- **State Management**: RxJS + Services (Angular standard)
- **HTTP Client**: Angular HttpClient
- **WebSocket**: RxJS WebSocket
- **Testing**: Jest + Angular Testing Library
- **Build Tool**: Angular CLI with esbuild
- **Styling**: SCSS + Angular Material theming

## Architecture Decisions

### Standalone Components
- Use Angular's modern standalone API (no NgModules)
- Simpler dependency injection
- Better tree-shaking and bundle size
- Easier testing

### RxJS + Services Pattern
- Services for business logic and state
- BehaviorSubject for shared state
- Observables for async operations
- Reactive forms for user input

### Feature-Based Structure
```
src/app/
├── core/                 # Singleton services, guards, interceptors
│   ├── services/
│   │   ├── api.service.ts
│   │   ├── websocket.service.ts
│   │   └── auth.service.ts
│   ├── interceptors/
│   │   └── api.interceptor.ts
│   └── guards/
│       └── auth.guard.ts
├── shared/              # Shared components, directives, pipes
│   ├── components/
│   ├── directives/
│   └── pipes/
├── features/            # Feature modules
│   ├── projects/
│   ├── workflow/
│   ├── checkpoints/
│   ├── images/
│   └── story-bible/
└── app.component.ts
```

---

## Task 16: Set Up Angular Project

### Objectives

Initialize Angular v22 project with TypeScript, Angular Material, and development tooling.

### Implementation Steps

1. **Create Angular Project**
```bash
npx @angular/cli@22 new web --routing --style=scss --standalone
cd web
```

2. **Install Dependencies**
```bash
# Angular Material
ng add @angular/material

# Additional dependencies
npm install rxjs@^7.8.0
npm install @ngrx/component-store  # Optional: for local component state
npm install date-fns  # Date utilities

# Dev dependencies
npm install -D jest @types/jest jest-preset-angular
npm install -D @angular-eslint/eslint-plugin
npm install -D prettier eslint-config-prettier
```

3. **Configure Jest**
```typescript
// jest.config.js
module.exports = {
  preset: 'jest-preset-angular',
  setupFilesAfterEnv: ['<rootDir>/setup-jest.ts'],
  testPathIgnorePatterns: ['/node_modules/', '/dist/'],
  coverageDirectory: 'coverage',
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.spec.ts',
    '!src/main.ts',
    '!src/polyfills.ts'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

4. **Create Core Services**

**API Service** (`src/app/core/services/api.service.ts`):
```typescript
import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  get<T>(endpoint: string, params?: HttpParams): Observable<T> {
    return this.http.get<T>(`${this.baseUrl}${endpoint}`, { params });
  }

  post<T>(endpoint: string, body: any): Observable<T> {
    return this.http.post<T>(`${this.baseUrl}${endpoint}`, body);
  }

  patch<T>(endpoint: string, body: any): Observable<T> {
    return this.http.patch<T>(`${this.baseUrl}${endpoint}`, body);
  }

  delete<T>(endpoint: string): Observable<T> {
    return this.http.delete<T>(`${this.baseUrl}${endpoint}`);
  }
}
```

**WebSocket Service** (`src/app/core/services/websocket.service.ts`):
```typescript
import { Injectable } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { Observable, Subject, timer } from 'rxjs';
import { retry, tap, delayWhen } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

export interface WebSocketMessage {
  type: string;
  data?: any;
  timestamp?: string;
}

@Injectable({
  providedIn: 'root'
})
export class WebSocketService {
  private socket$: WebSocketSubject<WebSocketMessage> | null = null;
  private messagesSubject$ = new Subject<WebSocketMessage>();
  public messages$ = this.messagesSubject$.asObservable();

  connect(projectId: string): void {
    if (!this.socket$ || this.socket$.closed) {
      const wsUrl = `${environment.wsUrl}/ws/${projectId}`;
      
      this.socket$ = webSocket<WebSocketMessage>({
        url: wsUrl,
        openObserver: {
          next: () => console.log('WebSocket connected')
        },
        closeObserver: {
          next: () => console.log('WebSocket disconnected')
        }
      });

      this.socket$
        .pipe(
          retry({
            delay: (error, retryCount) => {
              console.log(`Retry attempt ${retryCount}`);
              return timer(Math.min(1000 * Math.pow(2, retryCount), 30000));
            }
          }),
          tap({
            error: error => console.error('WebSocket error:', error)
          })
        )
        .subscribe(msg => this.messagesSubject$.next(msg));
    }
  }

  send(message: WebSocketMessage): void {
    if (this.socket$) {
      this.socket$.next(message);
    }
  }

  disconnect(): void {
    if (this.socket$) {
      this.socket$.complete();
      this.socket$ = null;
    }
  }
}
```

5. **Configure Environment**
```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api',
  wsUrl: 'ws://localhost:8000'
};

// src/environments/environment.prod.ts
export const environment = {
  production: true,
  apiUrl: '/api',
  wsUrl: `ws://${window.location.host}`
};
```

6. **Create Material Theme**
```scss
// src/styles.scss
@use '@angular/material' as mat;

@include mat.core();

$primary: mat.define-palette(mat.$indigo-palette);
$accent: mat.define-palette(mat.$pink-palette, A200, A100, A400);
$warn: mat.define-palette(mat.$red-palette);

$theme: mat.define-light-theme((
  color: (
    primary: $primary,
    accent: $accent,
    warn: $warn,
  ),
  typography: mat.define-typography-config(),
  density: 0,
));

@include mat.all-component-themes($theme);

// Custom styles
body {
  margin: 0;
  font-family: Roboto, "Helvetica Neue", sans-serif;
}
```

### Acceptance Criteria

- [x] Angular v22 project created
- [x] Angular Material installed and configured
- [x] Jest configured for testing
- [x] Core services created (API, WebSocket)
- [x] Environment configuration set up
- [x] Material theme configured
- [x] Dev server runs successfully

### Verification

```bash
# Start dev server
npm start

# Run tests
npm test

# Build for production
npm run build

# Lint code
npm run lint
```

**Manual checks:**
- [x] Navigate to http://localhost:4200
- [x] Verify Angular Material theme applied
- [x] Check browser console for errors
- [x] Verify API service can make requests
- [x] Verify WebSocket service can connect

---

## Task 17: Build Project Management UI

### Objectives

Create CRUD interface for managing projects with list, create, detail, edit, and delete functionality.

### File Structure

```
src/app/features/projects/
├── components/
│   ├── project-list/
│   │   ├── project-list.component.ts
│   │   ├── project-list.component.html
│   │   ├── project-list.component.scss
│   │   └── project-list.component.spec.ts
│   ├── project-form/
│   │   ├── project-form.component.ts
│   │   ├── project-form.component.html
│   │   ├── project-form.component.scss
│   │   └── project-form.component.spec.ts
│   ├── project-detail/
│   │   ├── project-detail.component.ts
│   │   ├── project-detail.component.html
│   │   ├── project-detail.component.scss
│   │   └── project-detail.component.spec.ts
│   └── project-card/
│       ├── project-card.component.ts
│       ├── project-card.component.html
│       ├── project-card.component.scss
│       └── project-card.component.spec.ts
├── services/
│   ├── project.service.ts
│   └── project.service.spec.ts
├── models/
│   └── project.model.ts
└── projects.routes.ts
```

### Implementation

**Project Model** (`models/project.model.ts`):
```typescript
export interface Project {
  id: string;
  name: string;
  genre?: string;
  target_length: number;
  status: 'draft' | 'in_progress' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  name: string;
  genre?: string;
  target_length?: number;
}

export interface ProjectUpdate {
  name?: string;
  genre?: string;
  target_length?: number;
  status?: string;
}

export interface ProjectListResponse {
  projects: Project[];
  total: number;
  page: number;
  page_size: number;
}
```

**Project Service** (`services/project.service.ts`):
```typescript
import { Injectable } from '@angular/core';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap } from 'rxjs/operators';
import { ApiService } from '../../../core/services/api.service';
import { Project, ProjectCreate, ProjectUpdate, ProjectListResponse } from '../models/project.model';

@Injectable({
  providedIn: 'root'
})
export class ProjectService {
  private projectsSubject = new BehaviorSubject<Project[]>([]);
  public projects$ = this.projectsSubject.asObservable();

  constructor(private api: ApiService) {}

  getProjects(page: number = 1, pageSize: number = 20): Observable<ProjectListResponse> {
    return this.api.get<ProjectListResponse>('/projects', { page, page_size: pageSize })
      .pipe(
        tap(response => this.projectsSubject.next(response.projects))
      );
  }

  getProject(id: string): Observable<Project> {
    return this.api.get<Project>(`/projects/${id}`);
  }

  createProject(data: ProjectCreate): Observable<Project> {
    return this.api.post<Project>('/projects', data)
      .pipe(
        tap(project => {
          const current = this.projectsSubject.value;
          this.projectsSubject.next([project, ...current]);
        })
      );
  }

  updateProject(id: string, data: ProjectUpdate): Observable<Project> {
    return this.api.patch<Project>(`/projects/${id}`, data)
      .pipe(
        tap(updated => {
          const current = this.projectsSubject.value;
          const index = current.findIndex(p => p.id === id);
          if (index !== -1) {
            current[index] = updated;
            this.projectsSubject.next([...current]);
          }
        })
      );
  }

  deleteProject(id: string): Observable<void> {
    return this.api.delete<void>(`/projects/${id}`)
      .pipe(
        tap(() => {
          const current = this.projectsSubject.value;
          this.projectsSubject.next(current.filter(p => p.id !== id));
        })
      );
  }
}
```

**Project List Component** (`components/project-list/project-list.component.ts`):
```typescript
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { Observable } from 'rxjs';
import { ProjectService } from '../../services/project.service';
import { Project } from '../../models/project.model';
import { ProjectCardComponent } from '../project-card/project-card.component';

@Component({
  selector: 'app-project-list',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    MatIconModule,
    ProjectCardComponent
  ],
  template: `
    <div class="project-list-container">
      <div class="header">
        <h1>Projects</h1>
        <button mat-raised-button color="primary" (click)="createProject()">
          <mat-icon>add</mat-icon>
          New Project
        </button>
      </div>

      <div class="projects-grid" *ngIf="projects$ | async as projects; else loading">
        <app-project-card
          *ngFor="let project of projects"
          [project]="project"
          (click)="viewProject(project.id)"
          (delete)="deleteProject($event)">
        </app-project-card>
      </div>

      <ng-template #loading>
        <div class="loading">
          <mat-spinner></mat-spinner>
        </div>
      </ng-template>
    </div>
  `,
  styles: [`
    .project-list-container {
      padding: 24px;
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }

    .projects-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 16px;
    }

    .loading {
      display: flex;
      justify-content: center;
      padding: 48px;
    }
  `]
})
export class ProjectListComponent implements OnInit {
  projects$: Observable<Project[]>;

  constructor(
    private projectService: ProjectService,
    private router: Router
  ) {
    this.projects$ = this.projectService.projects$;
  }

  ngOnInit(): void {
    this.projectService.getProjects().subscribe();
  }

  createProject(): void {
    this.router.navigate(['/projects/new']);
  }

  viewProject(id: string): void {
    this.router.navigate(['/projects', id]);
  }

  deleteProject(id: string): void {
    if (confirm('Are you sure you want to delete this project?')) {
      this.projectService.deleteProject(id).subscribe();
    }
  }
}
```

### Acceptance Criteria

- [x] Can view list of projects
- [x] Can create new project
- [x] Can view project details
- [x] Can edit project
- [x] Can delete project
- [x] Loading states shown
- [x] Errors displayed to user
- [x] Responsive design
- [x] Tests pass

### Verification

```bash
# Run component tests
npm test -- --testPathPattern=projects

# Run e2e tests
npm run e2e
```

---

## Task 18: Build Workflow Execution UI

### Objectives

Create real-time workflow monitoring interface with WebSocket integration for live progress updates.

### Components

1. **WorkflowExecutor** - Main workflow control component
2. **AgentStatus** - Individual agent status display
3. **PhaseIndicator** - Current phase visualization
4. **ProgressTracker** - Overall progress bar

### Implementation

**Workflow Service** (`services/workflow.service.ts`):
```typescript
import { Injectable } from '@angular/core';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap } from 'rxjs/operators';
import { ApiService } from '../../../core/services/api.service';
import { WebSocketService } from '../../../core/services/websocket.service';

export interface WorkflowStatus {
  id: string;
  project_id: string;
  status: 'running' | 'paused' | 'completed' | 'failed' | 'cancelled';
  current_phase: string;
  current_agent: string | null;
  progress_percentage: number;
  completed_steps: number;
  total_steps: number;
  started_at: string;
  paused_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}

@Injectable({
  providedIn: 'root'
})
export class WorkflowService {
  private statusSubject = new BehaviorSubject<WorkflowStatus | null>(null);
  public status$ = this.statusSubject.asObservable();

  constructor(
    private api: ApiService,
    private ws: WebSocketService
  ) {
    // Subscribe to WebSocket messages
    this.ws.messages$.subscribe(msg => {
      if (msg.type === 'progress' || msg.type === 'status') {
        this.handleProgressUpdate(msg.data);
      }
    });
  }

  startWorkflow(projectId: string): Observable<WorkflowStatus> {
    return this.api.post<WorkflowStatus>(`/workflow/${projectId}/start`, {})
      .pipe(
        tap(status => {
          this.statusSubject.next(status);
          this.ws.connect(projectId);
        })
      );
  }

  pauseWorkflow(projectId: string): Observable<WorkflowStatus> {
    return this.api.post<WorkflowStatus>(`/workflow/${projectId}/pause`, {})
      .pipe(tap(status => this.statusSubject.next(status)));
  }

  resumeWorkflow(projectId: string): Observable<WorkflowStatus> {
    return this.api.post<WorkflowStatus>(`/workflow/${projectId}/resume`, {})
      .pipe(tap(status => this.statusSubject.next(status)));
  }

  cancelWorkflow(projectId: string): Observable<WorkflowStatus> {
    return this.api.post<WorkflowStatus>(`/workflow/${projectId}/cancel`, {})
      .pipe(tap(status => this.statusSubject.next(status)));
  }

  getStatus(projectId: string): Observable<WorkflowStatus> {
    return this.api.get<WorkflowStatus>(`/workflow/${projectId}/status`)
      .pipe(tap(status => this.statusSubject.next(status)));
  }

  private handleProgressUpdate(data: any): void {
    const current = this.statusSubject.value;
    if (current) {
      this.statusSubject.next({ ...current, ...data });
    }
  }
}
```

### Acceptance Criteria

- [x] Can start workflow from UI
- [x] Real-time progress updates displayed
- [x] Agent status shown for each agent
- [x] Phase indicator shows current phase
- [x] Can pause/resume workflow
- [x] Can cancel workflow
- [x] Errors displayed to user
- [x] WebSocket reconnection works
- [x] Tests pass

---

## Task 19-21: Additional Features

Similar structure for:
- **Task 19**: Checkpoint Editing UI
- **Task 20**: Image Gallery UI
- **Task 21**: Story Bible Visualization UI

Each will follow the same pattern:
1. Create models
2. Create service
3. Create components
4. Add routing
5. Write tests

---

## Testing Strategy

### Unit Tests (Jest)
```typescript
// Example: project.service.spec.ts
describe('ProjectService', () => {
  let service: ProjectService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [ProjectService, ApiService]
    });
    service = TestBed.inject(ProjectService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  it('should fetch projects', () => {
    const mockProjects = { projects: [], total: 0, page: 1, page_size: 20 };
    
    service.getProjects().subscribe(response => {
      expect(response).toEqual(mockProjects);
    });

    const req = httpMock.expectOne('/api/projects?page=1&page_size=20');
    expect(req.request.method).toBe('GET');
    req.flush(mockProjects);
  });
});
```

### E2E Tests (Playwright)
```typescript
// e2e/projects.spec.ts
import { test, expect } from '@playwright/test';

test('should create a new project', async ({ page }) => {
  await page.goto('/projects');
  await page.click('text=New Project');
  await page.fill('input[name="name"]', 'Test Project');
  await page.fill('input[name="genre"]', 'Fantasy');
  await page.click('button[type="submit"]');
  await expect(page.locator('text=Test Project')).toBeVisible();
});
```

---

## Build & Deployment

### Development
```bash
npm start                 # Dev server at localhost:4200
npm test                  # Run unit tests
npm run test:watch        # Watch mode
npm run lint              # Lint code
```

### Production Build
```bash
npm run build             # Build for production
npm run build:stats       # Build with bundle analyzer
```

### Docker Integration
```dockerfile
# Dockerfile.web
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist/web /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## Summary

**Total Tasks**: 6 (Tasks 16-21)
**Estimated Time**: 2 weeks
**Key Technologies**: Angular 22, Material, RxJS, Jest
**Integration Points**: FastAPI backend, WebSocket real-time updates

This plan maintains the same functionality as the Next.js version but uses Angular's ecosystem and best practices.
