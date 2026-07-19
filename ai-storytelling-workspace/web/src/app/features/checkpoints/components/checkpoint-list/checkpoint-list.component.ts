import { Component, OnInit, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';
import { MatChipsModule } from '@angular/material/chips';
import { CheckpointService } from '../../services/checkpoint.service';
import { Checkpoint } from '../../models/checkpoint.model';

@Component({
  selector: 'app-checkpoint-list',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatTableModule,
    MatChipsModule
  ],
  template: `
    <div class="checkpoints-container">
      <div class="header">
        <button mat-icon-button (click)="goBack()" aria-label="Go back">
          <mat-icon>arrow_back</mat-icon>
        </button>
        <h1 class="mat-headline-3" style="margin: 0;">Project Checkpoints</h1>
      </div>

      <mat-card>
        <mat-card-content>
          @if (loading()) {
            <div class="loading">
              <mat-spinner diameter="48"></mat-spinner>
            </div>
          } @else {
            <div class="table-container">
              @if (checkpoints().length === 0) {
                <div class="empty-state">
                  <mat-icon>fact_check</mat-icon>
                  <p>No checkpoints available yet. Run the workflow to generate checkpoints.</p>
                </div>
              } @else {
                <table mat-table [dataSource]="checkpoints()" class="mat-elevation-z0">
                  
                  <ng-container matColumnDef="type">
                    <th mat-header-cell *matHeaderCellDef> Checkpoint Type </th>
                    <td mat-cell *matCellDef="let element"> {{ element.type | titlecase }} </td>
                  </ng-container>

                  <ng-container matColumnDef="status">
                    <th mat-header-cell *matHeaderCellDef> Status </th>
                    <td mat-cell *matCellDef="let element">
                      <mat-chip [color]="getStatusColor(element.status)" highlighted>
                        {{ element.status | titlecase }}
                      </mat-chip>
                    </td>
                  </ng-container>

                  <ng-container matColumnDef="updated_at">
                    <th mat-header-cell *matHeaderCellDef> Last Updated </th>
                    <td mat-cell *matCellDef="let element"> {{ element.updated_at | date:'short' }} </td>
                  </ng-container>

                  <ng-container matColumnDef="actions">
                    <th mat-header-cell *matHeaderCellDef> Actions </th>
                    <td mat-cell *matCellDef="let element">
                      <button mat-stroked-button color="primary" (click)="viewCheckpoint(element.id)">
                        Review
                      </button>
                    </td>
                  </ng-container>

                  <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
                  <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
                </table>
              }
            </div>
          }
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .checkpoints-container {
      padding: 24px;
      max-width: 1000px;
      margin: 0 auto;
    }

    .header {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 32px;
    }

    .table-container {
      width: 100%;
      overflow-x: auto;
    }

    table {
      width: 100%;
    }

    .loading {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 200px;
    }

    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 48px;
      color: rgba(0,0,0,0.6);
    }
    .empty-state mat-icon {
      font-size: 48px;
      height: 48px;
      width: 48px;
      margin-bottom: 16px;
    }
  `]
})
export class CheckpointListComponent implements OnInit {
  projectId = signal<string>('');
  checkpoints = signal<Checkpoint[]>([]);
  loading = signal<boolean>(true);
  displayedColumns: string[] = ['type', 'status', 'updated_at', 'actions'];

  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private checkpointService = inject(CheckpointService);

  ngOnInit(): void {
    const pId = this.route.snapshot.paramMap.get('id') || 
                this.route.parent?.snapshot.paramMap.get('id') || '';
    this.projectId.set(pId);
    if (pId) {
      this.checkpointService.getProjectCheckpoints(pId).subscribe({
        next: (data) => {
          this.checkpoints.set(data);
          this.loading.set(false);
        },
        error: (err) => {
          console.error('Error loading checkpoints', err);
          this.loading.set(false);
        }
      });
    } else {
      this.loading.set(false);
    }
  }

  goBack(): void {
    this.router.navigate(['/projects', this.projectId()]);
  }

  viewCheckpoint(id: string): void {
    this.router.navigate(['/projects', this.projectId(), 'checkpoints', id]);
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
