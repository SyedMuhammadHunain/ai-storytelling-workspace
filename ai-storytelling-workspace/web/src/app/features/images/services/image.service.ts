import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '../../../core/services/api.service';
import { ProjectImage, GenerateImageRequest } from '../models/image.model';

@Injectable({
  providedIn: 'root'
})
export class ImageService {
  constructor(private api: ApiService) {}

  getProjectImages(projectId: string): Observable<ProjectImage[]> {
    return this.api.get<ProjectImage[]>('/images/', { project_id: projectId });
  }

  generateImage(projectId: string, request: GenerateImageRequest): Observable<ProjectImage> {
    return this.api.post<ProjectImage>('/images/generate', { ...request, project_id: projectId });
  }
}
