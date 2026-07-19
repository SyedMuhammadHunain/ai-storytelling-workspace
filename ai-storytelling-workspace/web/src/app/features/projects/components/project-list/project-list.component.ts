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
        <h1 class="mat-headline-3" style="margin: 0;">Projects</h1>
        <button mat-flat-button color="primary" (click)="createProject()">
          <mat-icon>add</mat-icon>
          New Project
        </button>
      </div>

      @if (projects$ | async; as projects) {
        <div class="projects-grid">
          @if (projects.length === 0) {
            <div class="empty-state">
              <mat-icon class="empty-icon">library_books</mat-icon>
              <h2>No Projects Found</h2>
              <p>Create a new project to start your storytelling journey.</p>
            </div>
          }
          @for (project of projects; track project.id) {
            <app-project-card
              [project]="project"
              (cardClick)="viewProject($event)"
              (delete)="deleteProject($event)">
            </app-project-card>
          }
        </div>
      } @else {
        <div class="loading">
          <mat-spinner diameter="48"></mat-spinner>
        </div>
      }
    </div>
  `,
  styles: [`
    .project-list-container {
      padding: 24px;
      max-width: 1200px;
      margin: 0 auto;
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 32px;
    }

    .projects-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 24px;
    }

    .loading {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 200px;
    }

    .empty-state {
      grid-column: 1 / -1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 64px 24px;
      text-align: center;
      background-color: rgba(0,0,0,0.02);
      border-radius: 12px;
      border: 1px dashed rgba(0,0,0,0.12);
    }
    
    .empty-icon {
      font-size: 64px;
      height: 64px;
      width: 64px;
      color: rgba(0,0,0,0.38);
      margin-bottom: 16px;
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
