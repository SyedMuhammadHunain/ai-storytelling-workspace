import { Component, OnInit, OnDestroy, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatChipsModule } from '@angular/material/chips';
import { WorkflowService } from '../../services/workflow.service';
import { WorkflowState } from '../../models/workflow.model';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-workflow-execution',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressBarModule,
    MatChipsModule
  ],
  template: `
    @if (state$ | async; as state) {
      <div class="workflow-container">
        <div class="header">
          <button mat-icon-button (click)="goBack()" aria-label="Go back">
            <mat-icon>arrow_back</mat-icon>
          </button>
          <h1 class="mat-headline-3" style="margin: 0;">Workflow Execution</h1>
          <mat-chip [color]="getStatusColor(state.status)" highlighted class="status-chip">
            {{ state.status | titlecase }}
          </mat-chip>
        </div>

      <div class="control-panel">
        <mat-card>
          <mat-card-content class="panel-content">
            <div class="workflow-info">
              <div>
                <p class="mat-body-small label">Current Phase</p>
                <p class="mat-body-large value">{{ state.current_phase }}</p>
              </div>
              <div>
                <p class="mat-body-small label">Active Agent</p>
                <p class="mat-body-large value">{{ state.current_agent }}</p>
              </div>
            </div>

            <div class="actions">
              @if (state.status === 'idle' || state.status === 'completed') {
                <button mat-flat-button color="primary" (click)="start()">
                  <mat-icon>play_arrow</mat-icon> Start
                </button>
              }
              
              @if (state.status === 'running') {
                <button mat-flat-button color="accent" (click)="pause()">
                  <mat-icon>pause</mat-icon> Pause
                </button>
              }

              @if (state.status === 'paused' || state.status === 'failed') {
                <button mat-flat-button color="primary" (click)="resume()">
                  <mat-icon>play_arrow</mat-icon> Resume
                </button>
              }
            </div>
          </mat-card-content>
          
          <mat-progress-bar 
            [mode]="state.status === 'running' ? 'indeterminate' : 'determinate'" 
            [value]="state.progress">
          </mat-progress-bar>
        </mat-card>
      </div>

      <mat-card class="terminal-card">
        <mat-card-header>
          <mat-card-title>
            <mat-icon>terminal</mat-icon> Activity Logs
          </mat-card-title>
        </mat-card-header>
        <mat-card-content>
          <div class="terminal-window" #terminalWindow>
            @if (state.logs.length === 0) {
              <div class="empty-log">
                Waiting for workflow to start...
              </div>
            }
            @for (log of state.logs; track log) {
              <div class="log-entry">
                <span class="prompt">$</span> {{ log }}
              </div>
            }
          </div>
        </mat-card-content>
      </mat-card>
      </div>
    }
  `,
  styles: [`
    .workflow-container {
      padding: 24px;
      max-width: 1200px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 24px;
      height: calc(100vh - 48px);
    }

    .header {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    
    .status-chip {
      margin-left: auto;
    }

    .panel-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 16px;
    }

    @media (max-width: 768px) {
      .panel-content {
        flex-direction: column;
        align-items: stretch;
        gap: 16px;
      }
    }

    .workflow-info {
      display: flex;
      gap: 48px;
    }

    .label {
      color: rgba(0, 0, 0, 0.6);
      margin: 0 0 4px 0;
    }

    .value {
      margin: 0;
      font-weight: 500;
    }

    .actions {
      display: flex;
      gap: 12px;
    }

    .terminal-card {
      flex: 1;
      display: flex;
      flex-direction: column;
      min-height: 0;
    }

    .terminal-card mat-card-content {
      flex: 1;
      padding: 0;
      min-height: 0;
    }

    .terminal-window {
      background-color: #1e1e1e;
      color: #d4d4d4;
      font-family: 'Consolas', 'Courier New', monospace;
      padding: 16px;
      height: calc(100% - 32px);
      overflow-y: auto;
      border-radius: 0 0 4px 4px;
    }

    .log-entry {
      margin-bottom: 4px;
      line-height: 1.4;
      word-wrap: break-word;
    }

    .prompt {
      color: #4CAF50;
      margin-right: 8px;
    }

    .empty-log {
      color: #808080;
      font-style: italic;
    }
  `]
})
export class WorkflowExecutionComponent implements OnInit, OnDestroy, AfterViewChecked {
  @ViewChild('terminalWindow') private terminalWindow!: ElementRef;
  
  projectId!: string;
  state$: Observable<WorkflowState>;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private workflowService: WorkflowService
  ) {
    this.state$ = this.workflowService.state$;
  }

  ngOnInit(): void {
    // Note: If navigating from a child route under projects, we might need parent route
    // But since this route is '/projects/:id/workflow', the id is in the parent snapshot
    this.projectId = this.route.snapshot.paramMap.get('id') || 
                     this.route.parent?.snapshot.paramMap.get('id') || '';
                     
    if (this.projectId) {
      this.workflowService.connect(this.projectId);
    }
  }

  ngOnDestroy(): void {
    this.workflowService.disconnect();
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  private scrollToBottom(): void {
    try {
      if (this.terminalWindow) {
        this.terminalWindow.nativeElement.scrollTop = this.terminalWindow.nativeElement.scrollHeight;
      }
    } catch (err) {
      console.error('Scroll to bottom failed', err);
    }
  }

  goBack(): void {
    this.router.navigate(['/projects', this.projectId]);
  }

  start(): void {
    this.workflowService.startWorkflow(this.projectId).subscribe();
  }

  pause(): void {
    this.workflowService.pauseWorkflow(this.projectId).subscribe();
  }

  resume(): void {
    this.workflowService.resumeWorkflow(this.projectId).subscribe();
  }

  getStatusColor(status: string): string {
    switch(status) {
      case 'running': return 'primary';
      case 'completed': return 'primary'; // Or maybe an alternate color if available
      case 'failed': return 'warn';
      case 'paused': return 'accent';
      default: return 'primary';
    }
  }
}
