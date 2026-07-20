import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { ApiService } from '../../../core/services/api.service';
import { Project, ProjectCreate, ProjectUpdate, ProjectListResponse } from '../models/project.model';

@Injectable({
  providedIn: 'root'
})
export class ProjectService {
  private projectsSubject = new BehaviorSubject<Project[]>([]);
  public projects$ = this.projectsSubject.asObservable();

  constructor(private api: ApiService) {}

  getProjects(page: number = 1, pageSize: number = 20): Observable<ProjectListResponse> {
    return this.api.get<ProjectListResponse>('/projects/', { page, page_size: pageSize })
      .pipe(
        tap((response: ProjectListResponse) => this.projectsSubject.next(response.projects))
      );
  }

  getProject(id: string): Observable<Project> {
    return this.api.get<Project>(`/projects/${id}`);
  }

  createProject(data: ProjectCreate): Observable<Project> {
    return this.api.post<Project>('/projects/', data)
      .pipe(
        tap((project: Project) => {
          const current = this.projectsSubject.value;
          this.projectsSubject.next([project, ...current]);
        })
      );
  }

  updateProject(id: string, data: ProjectUpdate): Observable<Project> {
    return this.api.put<Project>(`/projects/${id}`, data)
      .pipe(
        tap((updated: Project) => {
          const current = this.projectsSubject.value;
          const index = current.findIndex(p => p.id === id);
          if (index !== -1) {
            current[index] = updated;
            this.projectsSubject.next([...current]);
          }
        })
      );
  }

  deleteProject(id: string): Observable<void> {
    return this.api.delete<void>(`/projects/${id}`)
      .pipe(
        tap(() => {
          const current = this.projectsSubject.value;
          this.projectsSubject.next(current.filter(p => p.id !== id));
        })
      );
  }
}
