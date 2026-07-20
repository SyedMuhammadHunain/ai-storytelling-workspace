import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, Subscription, of } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
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

  constructor(
    private api: ApiService,
    private ws: WebSocketService
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

    this.wsSubscription = this.ws.messages$.subscribe((msg: WebSocketMessage) => {
      this.handleWebSocketMessage(msg);
    });
  }

  disconnect(): void {
    if (this.wsSubscription) {
      this.wsSubscription.unsubscribe();
    }
    this.ws.disconnect();
  }

  startWorkflow(projectId: string): Observable<WorkflowActionResponse> {
    return this.api.post<WorkflowActionResponse>(`/workflow/${projectId}/start`, {}).pipe(
      tap(res => {
        if (res && res.status) {
          this.updateState({ status: res.status as WorkflowState['status'] });
        }
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
          this.updateState({ status: res.status as WorkflowState['status'] });
        }
      })
    );
  }

  getStatus(projectId: string): Observable<Partial<WorkflowState>> {
    return this.api.get<Partial<WorkflowState>>(`/workflow/${projectId}/status`).pipe(
      catchError(error => {
        // If workflow doesn't exist (404), just return idle state
        return of({ status: 'idle' } as Partial<WorkflowState>);
      })
    );
  }

  private handleWebSocketMessage(msg: WebSocketMessage): void {
    const currentState = this.stateSubject.value;
    
    switch (msg.type) {
      case 'workflow_update':
        if (msg.data) {
          this.updateState(msg.data);
        }
        break;
      case 'log':
        if (msg.data?.message) {
          const timestamp = msg.timestamp || new Date().toISOString();
          const logEntry = `[${new Date(timestamp).toLocaleTimeString()}] ${msg.data.message}`;
          this.stateSubject.next({
            ...currentState,
            logs: [...currentState.logs, logEntry]
          });
        }
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
