export interface ProjectImage {
  id: string;
  project_id: string;
  url: string;
  prompt: string;
  type: 'cover' | 'character' | 'scene';
  created_at: string;
}

export interface GenerateImageRequest {
  prompt: string;
  type: 'cover' | 'character' | 'scene';
}

export interface ImageListResponse {
  images: ProjectImage[];
  total: number;
  by_type: Record<string, number>;
}
