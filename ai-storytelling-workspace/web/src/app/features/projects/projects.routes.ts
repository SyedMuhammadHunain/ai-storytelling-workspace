import { Routes } from '@angular/router';

export const PROJECT_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./components/project-list/project-list.component').then(m => m.ProjectListComponent),
    title: 'Projects'
  },
  {
    path: 'new',
    loadComponent: () => import('./components/project-form/project-form.component').then(m => m.ProjectFormComponent),
    title: 'New Project'
  },
  {
    path: ':id',
    loadComponent: () => import('./components/project-detail/project-detail.component').then(m => m.ProjectDetailComponent),
    title: 'Project Details'
  },
  {
    path: ':id/edit',
    loadComponent: () => import('./components/project-form/project-form.component').then(m => m.ProjectFormComponent),
    title: 'Edit Project'
  },
  {
    path: ':id/workflow',
    loadComponent: () => import('../workflow/components/workflow-execution/workflow-execution.component').then(m => m.WorkflowExecutionComponent),
    title: 'Workflow Execution'
  },
  {
    path: ':id/checkpoints',
    loadComponent: () => import('../checkpoints/components/checkpoint-list/checkpoint-list.component').then(m => m.CheckpointListComponent),
    title: 'Project Checkpoints'
  },
  {
    path: ':id/checkpoints/:checkpointId',
    loadComponent: () => import('../checkpoints/components/checkpoint-editor/checkpoint-editor.component').then(m => m.CheckpointEditorComponent),
    title: 'Edit Checkpoint'
  },
  {
    path: ':id/images',
    loadComponent: () => import('../images/components/image-gallery/image-gallery.component').then(m => m.ImageGalleryComponent),
    title: 'Image Gallery'
  },
  {
    path: ':id/story-bible',
    loadComponent: () => import('../bible/components/story-bible/story-bible.component').then(m => m.StoryBibleComponent),
    title: 'Story Bible'
  }
];
