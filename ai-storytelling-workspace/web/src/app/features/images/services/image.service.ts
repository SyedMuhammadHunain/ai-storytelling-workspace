import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { ApiService } from '../../../core/services/api.service';
import { ProjectImage, GenerateImageRequest, ImageListResponse } from '../models/image.model';

@Injectable({
  providedIn: 'root'
})
export class ImageService {
  constructor(private api: ApiService) {}

  getProjectImages(projectId: string): Observable<ProjectImage[]> {
    return this.api.get<ImageListResponse>('/images/', { project_id: projectId }).pipe(
      map(response => response.images)
    );
  }

  generateImage(projectId: string, request: GenerateImageRequest): Observable<ProjectImage> {
    return this.api.post<ProjectImage>('/images/generate', { ...request, project_id: projectId });
  }
}
