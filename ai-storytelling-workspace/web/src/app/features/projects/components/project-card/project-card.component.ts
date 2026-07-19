import { Component, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { Project } from '../../models/project.model';

@Component({
  selector: 'app-project-card',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule, MatIconModule, MatChipsModule],
  template: `
    <mat-card class="project-card" (click)="onClick()">
      <mat-card-header>
        <mat-card-title>{{ project().name }}</mat-card-title>
        <mat-card-subtitle>{{ project().genre || 'Unspecified Genre' }}</mat-card-subtitle>
      </mat-card-header>
      
      <mat-card-content>
        <div class="project-details">
          <p><strong>Target:</strong> {{ project().target_length | number }} words</p>
          <mat-chip-set>
            <mat-chip [color]="getStatusColor(project().status)" highlighted>
              {{ project().status | titlecase }}
            </mat-chip>
          </mat-chip-set>
          <p class="date-text">Updated: {{ project().updated_at | date:'short' }}</p>
        </div>
      </mat-card-content>

      <mat-card-actions align="end">
        <button mat-button color="warn" (click)="onDelete($event)">
          <mat-icon>delete</mat-icon>
          Delete
        </button>
      </mat-card-actions>
    </mat-card>
  `,
  styles: [`
    .project-card {
      cursor: pointer;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
      height: 100%;
      display: flex;
      flex-direction: column;
    }
    .project-card:hover {
      transform: translateY(-4px);
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .project-details {
      margin-top: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .date-text {
      color: rgba(0, 0, 0, 0.6);
      font-size: 0.85rem;
      margin: 0;
    }
    mat-card-content {
      flex-grow: 1;
    }
  `]
})
export class ProjectCardComponent {
  project = input.required<Project>();
  cardClick = output<string>();
  delete = output<string>();

  onClick() {
    this.cardClick.emit(this.project().id);
  }

  onDelete(event: Event) {
    event.stopPropagation();
    this.delete.emit(this.project().id);
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
