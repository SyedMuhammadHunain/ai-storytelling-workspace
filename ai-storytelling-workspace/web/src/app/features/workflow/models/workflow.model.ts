export interface WorkflowState {
  project_id: string;
  current_phase: string;
  current_agent: string;
  status: 'idle' | 'running' | 'paused' | 'failed' | 'completed' | 'cancelled';
  progress: number;
  logs: string[];
  error_message?: string;
}

export interface WorkflowActionResponse {
  status: string;
  message: string;
}
