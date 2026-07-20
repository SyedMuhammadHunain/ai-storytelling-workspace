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
    return this.api.get<any>('/images/', { project_id: projectId }).pipe(
      map(response => {
        const items = Array.isArray(response) ? response : (response?.images || []);
        return items.map((img: any) => ({
          ...img,
          url: img.url || img.file_path || '',
          type: img.type || (img.image_type === 'cover_art' ? 'cover' : 
                img.image_type === 'character_portrait' ? 'character' : 'scene')
        }));
      })
    );
  }

  generateImage(projectId: string, request: GenerateImageRequest): Observable<ProjectImage> {
    return this.api.post<any>('/images/generate', { ...request, project_id: projectId }).pipe(
      map(response => ({
        id: response.image_id || response.id || crypto.randomUUID(),
        project_id: projectId,
        url: response.url || response.file_path || 'assets/placeholder.png',
        prompt: request.prompt,
        type: request.type as 'cover'|'character'|'scene',
        created_at: new Date().toISOString()
      }))
    );
  }
}
