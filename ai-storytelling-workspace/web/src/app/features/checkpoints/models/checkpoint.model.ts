export interface Checkpoint {
  id: string;
  project_id: string;
  type: string; // e.g., 'brief', 'concept', 'story_bible', 'outline'
  content: any; // JSON object or string content
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
  updated_at: string;
}

export interface CheckpointUpdate {
  content?: any;
  status?: string;
}
