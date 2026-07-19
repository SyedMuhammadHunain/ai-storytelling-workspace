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
    return this.api.get<ProjectImage[]>(`/projects/${projectId}/images`);
  }

  generateImage(projectId: string, request: GenerateImageRequest): Observable<ProjectImage> {
    return this.api.post<ProjectImage>(`/projects/${projectId}/images/generate`, request);
  }
}
