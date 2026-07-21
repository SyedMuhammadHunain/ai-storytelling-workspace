import { Injectable, NgZone } from '@angular/core';
import { BehaviorSubject, Observable, Subscription, interval, of } from 'rxjs';
import { catchError, switchMap, takeWhile, tap } from 'rxjs/operators';
import { ApiService } from '../../../core/services/api.service';
import { WebSocketService, WebSocketMessage } from '../../../core/services/websocket.service';
import { WorkflowState, WorkflowActionResponse } from '../models/workflow.model';

@Injectable({
  providedIn: 'root'
})
export class WorkflowService {
  private stateSubject = new BehaviorSubject<WorkflowState>({
    project_id: '',
    current_phase: 'Initialization',
    current_agent: 'None',
    status: 'idle',
    progress: 0,
    logs: []
  });
  
  public state$ = this.stateSubject.asObservable();
  private wsSubscription?: Subscription;
  private pollingSubscription?: Subscription;

  constructor(
    private api: ApiService,
    private ws: WebSocketService,
    private ngZone: NgZone
  ) {}

  connect(projectId: string): void {
    // Reset state for new project
    this.stateSubject.next({
      project_id: projectId,
      current_phase: 'Initialization',
      current_agent: 'None',
      status: 'idle',
      progress: 0,
      logs: []
    });

    this.ws.connect(projectId);
    
    // Fetch initial status
    this.getStatus(projectId).subscribe(status => {
      this.updateState(status);
    });

    // Subscribe to WebSocket messages
    this.wsSubscription = this.ws.messages$.subscribe((msg: WebSocketMessage) => {
      this.handleWebSocketMessage(msg);
    });

    // Subscribe to WebSocket connection failures
    this.ws.connectionFailed$.subscribe(() => {
      const current = this.stateSubject.value;
      if (current.status === 'running' || current.status === 'paused') {
        this.updateState({
          status: 'failed',
          error_message: 'Lost connection to server. The workflow may have crashed.'
        });
        const timestamp = new Date().toLocaleTimeString();
        this.stateSubject.next({
          ...this.stateSubject.value,
          logs: [...this.stateSubject.value.logs, `[${timestamp}] ERROR: WebSocket connection lost after max retries.`]
        });
      }
    });

    // Start polling as a fallback for missed WebSocket messages
    this.startPolling(projectId);
  }

  disconnect(): void {
    if (this.wsSubscription) {
      this.wsSubscription.unsubscribe();
      this.wsSubscription = undefined;
    }
    if (this.pollingSubscription) {
      this.pollingSubscription.unsubscribe();
      this.pollingSubscription = undefined;
    }
    this.ws.disconnect();
  }

  startWorkflow(projectId: string): Observable<WorkflowActionResponse> {
    return this.api.post<WorkflowActionResponse>(`/workflow/${projectId}/start`, {}).pipe(
      tap(res => {
        if (res && res.status) {
          this.updateState({
            status: res.status as WorkflowState['status'],
            error_message: undefined
          });
        }
      }),
      catchError(error => {
        this.updateState({
          status: 'failed',
          error_message: error?.error?.detail || error?.message || 'Failed to start workflow'
        });
        throw error;
      })
    );
  }

  pauseWorkflow(projectId: string): Observable<WorkflowActionResponse> {
    return this.api.post<WorkflowActionResponse>(`/workflow/${projectId}/pause`, {}).pipe(
      tap(res => {
        if (res && res.status) {
          this.updateState({ status: res.status as WorkflowState['status'] });
        }
      })
    );
  }

  resumeWorkflow(projectId: string): Observable<WorkflowActionResponse> {
    return this.api.post<WorkflowActionResponse>(`/workflow/${projectId}/resume`, {}).pipe(
      tap(res => {
        if (res && res.status) {
          this.updateState({
            status: res.status as WorkflowState['status'],
            error_message: undefined
          });
        }
      })
    );
  }

  getStatus(projectId: string): Observable<Partial<WorkflowState>> {
    return this.api.get<Partial<WorkflowState>>(`/workflow/${projectId}/status`).pipe(
      catchError(error => {
        // Only treat 404 as idle (workflow doesn't exist yet)
        if (error.status === 404) {
          return of({ status: 'idle' } as Partial<WorkflowState>);
        }
        // All other errors (500, network, etc.) mean something went wrong
        return of({
          status: 'failed',
          error_message: error?.error?.detail || error?.message || 'Failed to fetch workflow status'
        } as Partial<WorkflowState>);
      })
    );
  }

  private startPolling(projectId: string): void {
    if (this.pollingSubscription) {
      this.pollingSubscription.unsubscribe();
    }

    // Poll every 5 seconds while the workflow is in a non-terminal state
    this.pollingSubscription = interval(5000).pipe(
      takeWhile(() => {
        const status = this.stateSubject.value.status;
        return status === 'running' || status === 'paused' || status === 'idle';
      }),
      switchMap(() => this.getStatus(projectId))
    ).subscribe(status => {
      if (status && Object.keys(status).length > 0) {
        this.updateState(status);
      }
    });
  }

  private handleWebSocketMessage(msg: any): void {
    const currentState = this.stateSubject.value;
    const timestamp = msg.timestamp || new Date().toISOString();
    const timeStr = new Date(timestamp).toLocaleTimeString();
    
    // Map backend payload to frontend state
    const newState: Partial<WorkflowState> = {};
    if (msg.status) newState.status = msg.status as any;
    if (msg.phase) newState.current_phase = msg.phase;
    if (msg.agent) newState.current_agent = msg.agent;
    if (msg.progress !== undefined) newState.progress = msg.progress;
    if (msg.error_message) newState.error_message = msg.error_message;

    switch (msg.type) {
      case 'connected':
        if (msg.message) {
          newState.logs = [...currentState.logs, `[${timeStr}] ${msg.message}`];
        }
        this.updateState(newState);
        break;
        
      case 'progress':
      case 'status':
      case 'workflow_update':
        if (msg.message) {
          newState.logs = [...currentState.logs, `[${timeStr}] ${msg.message}`];
        }
        this.updateState(newState);
        break;
        
      case 'log':
        if (msg.message || (msg.data && msg.data.message)) {
          const text = msg.message || msg.data.message;
          this.stateSubject.next({
            ...currentState,
            logs: [...currentState.logs, `[${timeStr}] ${text}`]
          });
        }
        break;
        
      case 'error':
        const errorMsg = msg.error_message || msg.message || (msg.data && (msg.data.message || msg.data.error)) || 'An unknown error occurred';
        newState.status = 'failed';
        newState.error_message = errorMsg;
        newState.logs = [...currentState.logs, `[${timeStr}] ERROR: ${errorMsg}`];
        this.updateState(newState);
        break;
        
      case 'checkpoint':
        if (msg.message) {
          newState.logs = [...currentState.logs, `[${timeStr}] CHECKPOINT: ${msg.message}`];
        }
        this.updateState(newState);
        break;
    }
  }

  private updateState(partialState: Partial<WorkflowState>): void {
    const currentState = this.stateSubject.value;
    this.stateSubject.next({
      ...currentState,
      ...partialState
    });
  }
}
