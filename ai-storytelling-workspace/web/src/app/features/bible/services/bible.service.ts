import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { ApiService } from '../../../core/services/api.service';
import { StoryBible } from '../models/bible.model';

@Injectable({
  providedIn: 'root'
})
export class BibleService {
  constructor(private api: ApiService) {}

  getStoryBible(projectId: string): Observable<StoryBible> {
    return this.api.get<any>(`/story-bible/project/${projectId}/latest`).pipe(
      map(data => ({
        ...data,
        characters: data.characters ? Object.values(data.characters) : [],
        locations: data.locations ? Object.values(data.locations) : [],
        plot_threads: data.plot_threads ? Object.values(data.plot_threads) : [],
        timeline: data.timeline || [],
        lore: data.terminology ? Object.entries(data.terminology).map(([topic, description]) => ({
          topic,
          description: Array.isArray(description) ? description.join(', ') : String(description)
        })) : []
      } as StoryBible))
    );
  }
}
