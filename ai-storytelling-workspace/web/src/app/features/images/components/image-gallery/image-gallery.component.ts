import { Component, OnInit, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { ImageService } from '../../services/image.service';
import { ProjectImage } from '../../models/image.model';

@Component({
  selector: 'app-image-gallery',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatChipsModule,
    MatSnackBarModule
  ],
  template: `
    <div class="gallery-container">
      <div class="header">
        <button mat-icon-button (click)="goBack()" aria-label="Go back">
          <mat-icon>arrow_back</mat-icon>
        </button>
        <h1 class="mat-headline-3" style="margin: 0;">Image Gallery</h1>
      </div>

      <div class="generator-section">
        <mat-card>
          <mat-card-header>
            <mat-card-title>Generate New Image</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <form [formGroup]="generateForm" (ngSubmit)="generateImage()" class="generate-form">
              <mat-form-field appearance="outline" class="form-field prompt-field">
                <mat-label>Image Prompt</mat-label>
                <textarea matInput formControlName="prompt" placeholder="Describe the image..." rows="3" required></textarea>
              </mat-form-field>
              
              <div class="form-row">
                <mat-form-field appearance="outline" class="form-field">
                  <mat-label>Image Type</mat-label>
                  <mat-select formControlName="type" required>
                    <mat-option value="cover">Book Cover</mat-option>
                    <mat-option value="character">Character Portrait</mat-option>
                    <mat-option value="scene">Scene Illustration</mat-option>
                  </mat-select>
                </mat-form-field>

                @if (!generating()) {
                  <button mat-flat-button color="primary" type="submit" [disabled]="generateForm.invalid" class="generate-btn">
                    <mat-icon>auto_awesome</mat-icon>
                    <span>Generate</span>
                  </button>
                } @else {
                  <button mat-flat-button color="primary" type="submit" disabled class="generate-btn">
                    <mat-spinner diameter="20" class="btn-spinner"></mat-spinner>
                    <span>Generating...</span>
                  </button>
                }
              </div>
            </form>
          </mat-card-content>
        </mat-card>
      </div>

      @if (!loading()) {
        <div class="images-grid">
          @if (images().length === 0) {
            <div class="empty-state">
              <mat-icon>image_search</mat-icon>
              <p>No images generated yet. Use the form above to create one.</p>
            </div>
          }

          @for (img of images(); track img.url) {
            <mat-card class="image-card">
              <img mat-card-image [src]="img.url" [alt]="img.prompt" class="gallery-img">
              <mat-card-content class="image-content">
                <mat-chip-set>
                  <mat-chip [color]="getTypeColor(img.type)" highlighted size="small">
                    {{ img.type | titlecase }}
                  </mat-chip>
                </mat-chip-set>
                <p class="prompt-text">{{ img.prompt }}</p>
              </mat-card-content>
            </mat-card>
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
    .gallery-container {
      padding: 24px;
      max-width: 1200px;
      margin: 0 auto;
    }

    .header {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 24px;
    }

    .generator-section {
      margin-bottom: 32px;
    }

    .generate-form {
      display: flex;
      flex-direction: column;
      gap: 16px;
      padding-top: 16px;
    }

    .form-row {
      display: flex;
      gap: 16px;
      align-items: flex-start;
    }

    .form-field {
      flex: 1;
    }
    
    .prompt-field {
      width: 100%;
    }

    .generate-btn {
      height: 56px;
      padding: 0 24px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .btn-spinner {
      margin-right: 8px;
    }

    .images-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 24px;
    }

    .image-card {
      display: flex;
      flex-direction: column;
      height: 100%;
      overflow: hidden;
    }

    .gallery-img {
      width: 100%;
      height: 300px;
      object-fit: cover;
    }

    .image-content {
      padding: 16px;
      flex-grow: 1;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .prompt-text {
      margin: 0;
      color: rgba(0,0,0,0.87);
      font-size: 0.9rem;
      line-height: 1.4;
      display: -webkit-box;
      -webkit-line-clamp: 4;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .empty-state {
      grid-column: 1 / -1;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 64px;
      color: rgba(0,0,0,0.6);
      background-color: rgba(0,0,0,0.02);
      border-radius: 12px;
      border: 1px dashed rgba(0,0,0,0.12);
    }

    .empty-state mat-icon {
      font-size: 48px;
      height: 48px;
      width: 48px;
      margin-bottom: 16px;
    }

    .loading {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 200px;
    }
  `]
})
export class ImageGalleryComponent implements OnInit {
  projectId = signal<string>('');
  generateForm: FormGroup;
  generating = signal<boolean>(false);
  loading = signal<boolean>(true);
  
  images = signal<ProjectImage[]>([]);

  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private fb = inject(FormBuilder);
  private imageService = inject(ImageService);
  private snackBar = inject(MatSnackBar);

  constructor() {
    this.generateForm = this.fb.group({
      prompt: ['', Validators.required],
      type: ['scene', Validators.required]
    });
  }

  ngOnInit(): void {
    const pId = this.route.snapshot.paramMap.get('id') || 
                this.route.parent?.snapshot.paramMap.get('id') || '';
    this.projectId.set(pId);
                     
    if (pId) {
      this.loadImages();
    } else {
      this.loading.set(false);
    }
  }

  loadImages(): void {
    this.loading.set(true);
    this.imageService.getProjectImages(this.projectId()).subscribe({
      next: (data) => {
        this.images.set(data);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Failed to load images', err);
        this.loading.set(false);
        this.snackBar.open('Failed to load images', 'Close', { duration: 3000 });
      }
    });
  }

  generateImage(): void {
    if (this.generateForm.invalid) return;

    this.generating.set(true);
    const request = this.generateForm.value;

    this.imageService.generateImage(this.projectId(), request).subscribe({
      next: (newImage) => {
        this.images.update(current => [newImage, ...current]);
        this.generating.set(false);
        this.generateForm.reset({ type: 'scene' }); // Reset prompt, keep default type
        this.snackBar.open('Image generated successfully', 'Close', { duration: 3000 });
      },
      error: (err) => {
        console.error('Failed to generate image', err);
        this.generating.set(false);
        this.snackBar.open('Failed to generate image', 'Close', { duration: 3000 });
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/projects', this.projectId()]);
  }

  getTypeColor(type: string): string {
    switch(type) {
      case 'cover': return 'primary';
      case 'character': return 'accent';
      case 'scene': return 'warn'; // Or just default
      default: return 'primary';
    }
  }
}
