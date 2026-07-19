import { Component, OnInit, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatChipsModule } from '@angular/material/chips';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { CheckpointService } from '../../services/checkpoint.service';
import { Checkpoint } from '../../models/checkpoint.model';

@Component({
  selector: 'app-checkpoint-editor',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatFormFieldModule,
    MatInputModule,
    MatChipsModule,
    MatSnackBarModule
  ],
  template: `
    <div class="editor-container">
      @if (loading()) {
        <div class="loading">
          <mat-spinner diameter="48"></mat-spinner>
        </div>
      }

      @if (!loading() && checkpoint(); as currentCheckpoint) {
        <div class="header">
          <button mat-icon-button (click)="goBack()" aria-label="Go back">
            <mat-icon>arrow_back</mat-icon>
          </button>
          <div>
            <h1 class="mat-headline-3" style="margin: 0; display: inline-block;">
              Review: {{ currentCheckpoint.type | titlecase }}
            </h1>
            <mat-chip [color]="getStatusColor(currentCheckpoint.status)" highlighted style="margin-left: 16px;">
              {{ currentCheckpoint.status | titlecase }}
            </mat-chip>
          </div>
          <span class="spacer"></span>
          <div class="actions">
            <button mat-flat-button color="primary" [disabled]="saving()" (click)="saveContent()">
              <mat-icon>save</mat-icon> Save Changes
            </button>
            <button mat-flat-button color="accent" [disabled]="saving() || currentCheckpoint.status === 'approved'" (click)="approve()">
              <mat-icon>check_circle</mat-icon> Approve Checkpoint
            </button>
          </div>
        </div>

        <mat-card>
          <mat-card-content>
            <mat-form-field appearance="outline" class="full-width editor-field">
              <mat-label>Checkpoint Content (JSON)</mat-label>
              <textarea matInput [ngModel]="contentString()" (ngModelChange)="contentString.set($event)" rows="25"
                placeholder="Edit content here..." 
                style="font-family: monospace;">
              </textarea>
            </mat-form-field>
          </mat-card-content>
        </mat-card>
      }
    </div>
  `,
  styles: [`
    .editor-container {
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

    .spacer {
      flex: 1 1 auto;
    }

    .actions {
      display: flex;
      gap: 12px;
    }

    .full-width {
      width: 100%;
    }

    .editor-field {
      margin-top: 16px;
    }

    .loading {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 400px;
    }
  `]
})
export class CheckpointEditorComponent implements OnInit {
  projectId = signal<string>('');
  checkpointId = signal<string>('');
  checkpoint = signal<Checkpoint | undefined>(undefined);
  contentString = signal<string>('');
  loading = signal<boolean>(true);
  saving = signal<boolean>(false);

  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private checkpointService = inject(CheckpointService);
  private snackBar = inject(MatSnackBar);

  ngOnInit(): void {
    const pId = this.route.snapshot.paramMap.get('id') || 
                this.route.parent?.snapshot.paramMap.get('id') || '';
    this.projectId.set(pId);
    
    const cId = this.route.snapshot.paramMap.get('checkpointId') || '';
    this.checkpointId.set(cId);

    if (cId) {
      this.loadCheckpoint();
    }
  }

  loadCheckpoint(): void {
    this.loading.set(true);
    this.checkpointService.getCheckpoint(this.checkpointId()).subscribe({
      next: (ckpt) => {
        this.checkpoint.set(ckpt);
        this.contentString.set(typeof ckpt.content === 'string' 
          ? ckpt.content 
          : JSON.stringify(ckpt.content, null, 2));
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Error loading checkpoint', err);
        this.loading.set(false);
        this.snackBar.open('Failed to load checkpoint', 'Close', { duration: 3000 });
      }
    });
  }

  saveContent(): void {
    const ckpt = this.checkpoint();
    if (!ckpt) return;

    this.saving.set(true);
    let parsedContent: any;
    try {
      parsedContent = JSON.parse(this.contentString());
    } catch (e) {
      parsedContent = this.contentString();
    }

    this.checkpointService.updateCheckpoint(this.checkpointId(), { content: parsedContent }).subscribe({
      next: (updated) => {
        this.checkpoint.set(updated);
        this.saving.set(false);
        this.snackBar.open('Checkpoint saved successfully', 'Close', { duration: 3000 });
      },
      error: (err) => {
        console.error('Error saving checkpoint', err);
        this.saving.set(false);
        this.snackBar.open('Failed to save checkpoint', 'Close', { duration: 3000 });
      }
    });
  }

  approve(): void {
    this.saving.set(true);
    this.checkpointService.approveCheckpoint(this.checkpointId()).subscribe({
      next: (updated) => {
        this.checkpoint.set(updated);
        this.saving.set(false);
        this.snackBar.open('Checkpoint approved successfully', 'Close', { duration: 3000 });
      },
      error: (err) => {
        console.error('Error approving checkpoint', err);
        this.saving.set(false);
        this.snackBar.open('Failed to approve checkpoint', 'Close', { duration: 3000 });
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/projects', this.projectId(), 'checkpoints']);
  }

  getStatusColor(status: string): string {
    switch(status) {
      case 'approved': return 'primary';
      case 'pending': return 'accent';
      case 'rejected': return 'warn';
      default: return 'primary';
    }
  }
}
