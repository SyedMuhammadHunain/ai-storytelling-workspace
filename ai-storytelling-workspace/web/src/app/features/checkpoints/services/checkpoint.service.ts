import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { ApiService } from '../../../core/services/api.service';
import { Checkpoint, CheckpointUpdate, CheckpointListResponse } from '../models/checkpoint.model';

@Injectable({
  providedIn: 'root'
})
export class CheckpointService {
  constructor(private api: ApiService) {}

  getProjectCheckpoints(projectId: string): Observable<Checkpoint[]> {
    return this.api.get<CheckpointListResponse>('/checkpoints/', { project_id: projectId }).pipe(
      map(response => response.checkpoints)
    );
  }

  getCheckpoint(id: string): Observable<Checkpoint> {
    return this.api.get<Checkpoint>(`/checkpoints/${id}`);
  }

  updateCheckpoint(id: string, data: CheckpointUpdate): Observable<Checkpoint> {
    return this.api.patch<Checkpoint>(`/checkpoints/${id}`, data);
  }

  approveCheckpoint(id: string): Observable<Checkpoint> {
    return this.api.post<Checkpoint>(`/checkpoints/${id}/approve`, {});
  }
}
