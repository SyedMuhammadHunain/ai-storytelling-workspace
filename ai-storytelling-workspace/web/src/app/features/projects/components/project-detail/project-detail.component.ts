import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatDividerModule } from '@angular/material/divider';
import { MatListModule } from '@angular/material/list';
import { ProjectService } from '../../services/project.service';
import { Project } from '../../models/project.model';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-project-detail',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatChipsModule,
    MatDividerModule,
    MatListModule
  ],
  template: `
    <div class="detail-container">
      <div class="header">
        <button mat-icon-button (click)="goBack()" aria-label="Go back">
          <mat-icon>arrow_back</mat-icon>
        </button>
        @if (project$ | async; as project) {
          <h1 class="mat-headline-3" style="margin: 0;">{{ project.name }}</h1>
          <span class="spacer"></span>
          <button mat-stroked-button (click)="editProject(project.id)">
            <mat-icon>edit</mat-icon> Edit
          </button>
        } @else {
          <h1 class="mat-headline-3" style="margin: 0;">Loading...</h1>
          <span class="spacer"></span>
        }
      </div>

      @if (project$ | async; as project) {
        <div class="content-grid">
          <div class="main-column">
            <mat-card class="info-card mb-4">
              <mat-card-header>
                <mat-card-title>Project Info</mat-card-title>
              </mat-card-header>
              <mat-card-content>
                <mat-list>
                  <mat-list-item>
                    <span matListItemTitle>Status</span>
                    <span matListItemLine>
                      <mat-chip [color]="getStatusColor(project.status)" highlighted>
                        {{ project.status | titlecase }}
                      </mat-chip>
                    </span>
                  </mat-list-item>
                  <mat-divider></mat-divider>
                  <mat-list-item>
                    <span matListItemTitle>Genre</span>
                    <span matListItemLine>{{ project.genre || 'Not specified' }}</span>
                  </mat-list-item>
                  <mat-divider></mat-divider>
                  <mat-list-item>
                    <span matListItemTitle>Target Length</span>
                    <span matListItemLine>{{ project.target_length | number }} words</span>
                  </mat-list-item>
                  <mat-divider></mat-divider>
                  <mat-list-item>
                    <span matListItemTitle>Created At</span>
                    <span matListItemLine>{{ project.created_at | date:'medium' }}</span>
                  </mat-list-item>
                </mat-list>
              </mat-card-content>
            </mat-card>
          </div>

          <div class="sidebar-column">
            <mat-card class="action-card mb-4">
              <mat-card-header>
                <mat-card-title>Workspace Tools</mat-card-title>
              </mat-card-header>
              <mat-card-content class="tools-content">
                <button mat-flat-button color="primary" class="full-width mb-2" (click)="navigateTo('workflow', project.id)">
                  <mat-icon>play_circle</mat-icon> Workflow Execution
                </button>
                <button mat-stroked-button class="full-width mb-2" (click)="navigateTo('story-bible', project.id)">
                  <mat-icon>menu_book</mat-icon> Story Bible
                </button>
                <button mat-stroked-button class="full-width mb-2" (click)="navigateTo('checkpoints', project.id)">
                  <mat-icon>fact_check</mat-icon> Checkpoints
                </button>
                <button mat-stroked-button class="full-width" (click)="navigateTo('images', project.id)">
                  <mat-icon>photo_library</mat-icon> Image Gallery
                </button>
              </mat-card-content>
            </mat-card>
          </div>
        </div>
      } @else {
        <div class="loading">
          <mat-spinner diameter="48"></mat-spinner>
        </div>
      }
    </div>
  `,
  styles: [`
    .detail-container {
      padding: 24px;
      max-width: 1200px;
      margin: 0 auto;
    }

    .header {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 32px;
    }

    .spacer {
      flex: 1 1 auto;
    }

    .content-grid {
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 24px;
    }

    @media (max-width: 768px) {
      .content-grid {
        grid-template-columns: 1fr;
      }
    }

    .mb-4 {
      margin-bottom: 16px;
    }

    .mb-2 {
      margin-bottom: 8px;
    }

    .full-width {
      width: 100%;
      display: flex;
      justify-content: flex-start;
    }

    .tools-content {
      display: flex;
      flex-direction: column;
      padding-top: 16px;
    }

    .loading {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 200px;
    }
  `]
})
export class ProjectDetailComponent implements OnInit {
  project$!: Observable<Project>;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private projectService: ProjectService
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.project$ = this.projectService.getProject(id);
    }
  }

  goBack(): void {
    this.router.navigate(['/projects']);
  }

  editProject(id: string): void {
    this.router.navigate(['/projects', id, 'edit']);
  }

  navigateTo(feature: string, id: string): void {
    this.router.navigate(['/projects', id, feature]);
  }

  getStatusColor(status: string): string {
    switch(status) {
      case 'completed': return 'primary';
      case 'in_progress': return 'accent';
      case 'failed': return 'warn';
      default: return 'primary';
    }
  }
}
