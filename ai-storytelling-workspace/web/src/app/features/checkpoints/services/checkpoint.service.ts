import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '../../../core/services/api.service';
import { Checkpoint, CheckpointUpdate } from '../models/checkpoint.model';

@Injectable({
  providedIn: 'root'
})
export class CheckpointService {
  constructor(private api: ApiService) {}

  getProjectCheckpoints(projectId: string): Observable<Checkpoint[]> {
    return this.api.get<Checkpoint[]>(`/projects/${projectId}/checkpoints`);
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
