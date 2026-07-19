import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ProjectService } from '../../services/project.service';
import { Project } from '../../models/project.model';

@Component({
  selector: 'app-project-form',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
    MatProgressSpinnerModule
  ],
  template: `
    <div class="form-container">
      <div class="header">
        <button mat-icon-button (click)="goBack()" aria-label="Go back">
          <mat-icon>arrow_back</mat-icon>
        </button>
        <h1 class="mat-headline-3" style="margin: 0;">{{ isEditMode ? 'Edit Project' : 'New Project' }}</h1>
      </div>

      <mat-card>
        <mat-card-content>
          @if (loading) {
            <div class="loading-overlay">
              <mat-spinner diameter="48"></mat-spinner>
            </div>
          }

          <form [formGroup]="projectForm" (ngSubmit)="onSubmit()" class="project-form">
            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Project Name</mat-label>
              <input matInput formControlName="name" placeholder="e.g., The Last Horizon" required>
              @if (projectForm.get('name')?.hasError('required')) {
                <mat-error>Project name is required</mat-error>
              }
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Genre</mat-label>
              <input matInput formControlName="genre" placeholder="e.g., Science Fiction">
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Target Length (words)</mat-label>
              <input matInput type="number" formControlName="target_length" min="1000" step="1000">
              @if (projectForm.get('target_length')?.hasError('min')) {
                <mat-error>Target length must be at least 1,000 words</mat-error>
              }
            </mat-form-field>

            <div class="form-actions">
              <button mat-button type="button" (click)="goBack()">Cancel</button>
              <button mat-flat-button color="primary" type="submit" [disabled]="projectForm.invalid || saving">
                {{ saving ? 'Saving...' : (isEditMode ? 'Save Changes' : 'Create Project') }}
              </button>
            </div>
          </form>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .form-container {
      padding: 24px;
      max-width: 600px;
      margin: 0 auto;
    }

    .header {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 32px;
    }

    .project-form {
      display: flex;
      flex-direction: column;
      gap: 16px;
      padding: 16px 0;
    }

    .full-width {
      width: 100%;
    }

    .form-actions {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      margin-top: 16px;
    }

    .loading-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(255, 255, 255, 0.7);
      z-index: 10;
      display: flex;
      justify-content: center;
      align-items: center;
    }
  `]
})
export class ProjectFormComponent implements OnInit {
  projectForm: FormGroup;
  isEditMode = false;
  projectId: string | null = null;
  loading = false;
  saving = false;

  constructor(
    private fb: FormBuilder,
    private projectService: ProjectService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.projectForm = this.fb.group({
      name: ['', Validators.required],
      genre: [''],
      target_length: [80000, [Validators.min(1000)]]
    });
  }

  ngOnInit(): void {
    this.projectId = this.route.snapshot.paramMap.get('id');
    if (this.projectId) {
      this.isEditMode = true;
      this.loadProject(this.projectId);
    }
  }

  loadProject(id: string): void {
    this.loading = true;
    this.projectService.getProject(id).subscribe({
      next: (project: Project) => {
        this.projectForm.patchValue({
          name: project.name,
          genre: project.genre,
          target_length: project.target_length
        });
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading project', err);
        this.loading = false;
        // Should probably show a snackbar here
      }
    });
  }

  onSubmit(): void {
    if (this.projectForm.valid) {
      this.saving = true;
      const formData = this.projectForm.value;
      
      const request$ = this.isEditMode && this.projectId
        ? this.projectService.updateProject(this.projectId, formData)
        : this.projectService.createProject(formData);
        
      request$.subscribe({
        next: () => {
          this.saving = false;
          this.router.navigate(['/projects']);
        },
        error: (err) => {
          console.error('Error saving project', err);
          this.saving = false;
          // Should probably show a snackbar here
        }
      });
    }
  }

  goBack(): void {
    this.router.navigate(['/projects']);
  }
}
