export interface Project {
  id: string;
  name: string;
  genre?: string;
  target_length: number;
  status: 'draft' | 'in_progress' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  name: string;
  genre?: string;
  target_length?: number;
}

export interface ProjectUpdate {
  name?: string;
  genre?: string;
  target_length?: number;
  status?: string;
}

export interface ProjectListResponse {
  projects: Project[];
  total: number;
  page: number;
  page_size: number;
}
