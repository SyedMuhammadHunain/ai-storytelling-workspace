export interface StoryBible {
  project_id: string;
  characters: BibleCharacter[];
  locations: BibleLocation[];
  plot_threads: BiblePlotThread[];
  timeline: BibleEvent[];
  lore: BibleLore[];
  updated_at: string;
}

export interface BibleCharacter {
  name: string;
  role: string;
  description: string;
  arc?: string;
  relationships?: Record<string, string>;
}

export interface BibleLocation {
  name: string;
  description: string;
  significance?: string;
}

export interface BiblePlotThread {
  name: string;
  description: string;
  status: string; // e.g., 'active', 'resolved'
}

export interface BibleEvent {
  date: string; // or order/timestamp
  event: string;
  description: string;
  characters_involved?: string[];
}

export interface BibleLore {
  topic: string;
  description: string;
}
