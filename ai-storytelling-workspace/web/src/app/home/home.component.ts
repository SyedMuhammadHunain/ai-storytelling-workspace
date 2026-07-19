import { Component } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-home',
  imports: [MatCardModule, MatButtonModule],
  template: `
    <div class="home-container">
      <mat-card>
        <mat-card-header>
          <mat-card-title>Welcome to AI Storytelling Workspace</mat-card-title>
        </mat-card-header>
        <mat-card-content>
          <p>A production-ready platform for generating complete novels with AI-powered text and images.</p>
          <p><strong>Features:</strong></p>
          <ul>
            <li>Real-time workflow monitoring</li>
            <li>Project management</li>
            <li>Checkpoint editing</li>
            <li>Image gallery</li>
            <li>Story Bible visualization</li>
          </ul>
        </mat-card-content>
        <mat-card-actions>
          <button mat-raised-button color="primary">Get Started</button>
        </mat-card-actions>
      </mat-card>
    </div>
  `,
  styles: [`
    .home-container {
      max-width: 800px;
      margin: 0 auto;
      padding: 24px;
    }

    mat-card {
      margin-bottom: 16px;
    }

    ul {
      margin: 16px 0;
      padding-left: 24px;
    }

    li {
      margin: 8px 0;
    }
  `]
})
export class HomeComponent {}