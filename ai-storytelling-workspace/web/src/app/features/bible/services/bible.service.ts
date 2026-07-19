import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '../../../core/services/api.service';
import { StoryBible } from '../models/bible.model';

@Injectable({
  providedIn: 'root'
})
export class BibleService {
  constructor(private api: ApiService) {}

  getStoryBible(projectId: string): Observable<StoryBible> {
    return this.api.get<StoryBible>(`/projects/${projectId}/bible`);
  }
}
