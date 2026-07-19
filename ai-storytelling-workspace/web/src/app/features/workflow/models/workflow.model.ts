export interface WorkflowState {
  project_id: string;
  current_phase: string;
  current_agent: string;
  status: 'idle' | 'running' | 'paused' | 'failed' | 'completed';
  progress: number;
  logs: string[];
}

export interface WorkflowActionResponse {
  status: string;
  message: string;
}
