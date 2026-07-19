import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTabsModule } from '@angular/material/tabs';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatChipsModule } from '@angular/material/chips';
import { MatListModule } from '@angular/material/list';
import { BibleService } from '../../services/bible.service';
import { StoryBible } from '../../models/bible.model';

@Component({
  selector: 'app-story-bible',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatTabsModule,
    MatExpansionModule,
    MatChipsModule,
    MatListModule
  ],
  template: `
    <div class="bible-container">
      <div class="header">
        <button mat-icon-button (click)="goBack()" aria-label="Go back">
          <mat-icon>arrow_back</mat-icon>
        </button>
        <h1 class="mat-headline-3" style="margin: 0;">Story Bible</h1>
        <span class="spacer"></span>
      </div>

      @if (bible(); as bible) {
        <mat-card class="bible-card">
          <mat-card-content style="padding: 0;">
            <mat-tab-group dynamicHeight backgroundColor="primary">
              
              <!-- Characters Tab -->
              <mat-tab label="Characters">
                <div class="tab-content">
                  @if (!bible.characters || bible.characters.length === 0) {
                    <div class="empty-state">
                      <p>No characters generated yet.</p>
                    </div>
                  }
                  
                  <mat-accordion>
                    @for (char of bible.characters; track char.name) {
                      <mat-expansion-panel>
                        <mat-expansion-panel-header>
                          <mat-panel-title>
                            <strong>{{ char.name }}</strong>
                          </mat-panel-title>
                          <mat-panel-description>
                            {{ char.role }}
                          </mat-panel-description>
                        </mat-expansion-panel-header>
                        <p>{{ char.description }}</p>
                        @if (char.arc) {
                          <div>
                            <strong>Character Arc:</strong>
                            <p>{{ char.arc }}</p>
                          </div>
                        }
                      </mat-expansion-panel>
                    }
                  </mat-accordion>
                </div>
              </mat-tab>

              <!-- Locations Tab -->
              <mat-tab label="Locations">
                <div class="tab-content">
                  @if (!bible.locations || bible.locations.length === 0) {
                    <div class="empty-state">
                      <p>No locations generated yet.</p>
                    </div>
                  }

                  <mat-accordion>
                    @for (loc of bible.locations; track loc.name) {
                      <mat-expansion-panel>
                        <mat-expansion-panel-header>
                          <mat-panel-title>
                            <strong>{{ loc.name }}</strong>
                          </mat-panel-title>
                        </mat-expansion-panel-header>
                        <p>{{ loc.description }}</p>
                        @if (loc.significance) {
                          <div>
                            <strong>Significance:</strong>
                            <p>{{ loc.significance }}</p>
                          </div>
                        }
                      </mat-expansion-panel>
                    }
                  </mat-accordion>
                </div>
              </mat-tab>

              <!-- Plot Threads Tab -->
              <mat-tab label="Plot Threads">
                <div class="tab-content">
                  @if (!bible.plot_threads || bible.plot_threads.length === 0) {
                    <div class="empty-state">
                      <p>No plot threads generated yet.</p>
                    </div>
                  }

                  <mat-accordion>
                    @for (thread of bible.plot_threads; track thread.name) {
                      <mat-expansion-panel>
                        <mat-expansion-panel-header>
                          <mat-panel-title>
                            <strong>{{ thread.name }}</strong>
                          </mat-panel-title>
                          <mat-panel-description>
                            <mat-chip-set>
                              <mat-chip highlighted size="small" [color]="thread.status === 'resolved' ? 'primary' : 'accent'">
                                {{ thread.status }}
                              </mat-chip>
                            </mat-chip-set>
                          </mat-panel-description>
                        </mat-expansion-panel-header>
                        <p>{{ thread.description }}</p>
                      </mat-expansion-panel>
                    }
                  </mat-accordion>
                </div>
              </mat-tab>

              <!-- Timeline Tab -->
              <mat-tab label="Timeline">
                <div class="tab-content">
                  @if (!bible.timeline || bible.timeline.length === 0) {
                    <div class="empty-state">
                      <p>No timeline events generated yet.</p>
                    </div>
                  }

                  <mat-list>
                    @for (event of bible.timeline; track event.event) {
                      <mat-list-item class="timeline-item">
                        <span matListItemTitle><strong>{{ event.date || 'Event' }}</strong>: {{ event.event }}</span>
                        <span matListItemLine class="multiline-text">{{ event.description }}</span>
                      </mat-list-item>
                    }
                  </mat-list>
                </div>
              </mat-tab>

              <!-- Lore Tab -->
              <mat-tab label="Lore">
                <div class="tab-content">
                  @if (!bible.lore || bible.lore.length === 0) {
                    <div class="empty-state">
                      <p>No lore generated yet.</p>
                    </div>
                  }

                  <mat-accordion>
                    @for (item of bible.lore; track item.topic) {
                      <mat-expansion-panel>
                        <mat-expansion-panel-header>
                          <mat-panel-title>
                            <strong>{{ item.topic }}</strong>
                          </mat-panel-title>
                        </mat-expansion-panel-header>
                        <p>{{ item.description }}</p>
                      </mat-expansion-panel>
                    }
                  </mat-accordion>
                </div>
              </mat-tab>

            </mat-tab-group>
          </mat-card-content>
        </mat-card>
      } @else {
        <div class="loading">
          <mat-spinner diameter="48"></mat-spinner>
        </div>
      }
    </div>
  `,
  styles: [`
    .bible-container {
      padding: 24px;
      max-width: 1000px;
      margin: 0 auto;
    }

    .header {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 24px;
    }

    .spacer {
      flex: 1 1 auto;
    }

    .bible-card {
      overflow: hidden;
    }

    .tab-content {
      padding: 24px;
      min-height: 400px;
      background-color: #fafafa;
    }

    .timeline-item {
      margin-bottom: 16px;
      height: auto !important; /* Override mat-list-item fixed height */
      padding: 8px 0;
    }

    .multiline-text {
      white-space: normal;
      line-height: 1.4;
      margin-top: 4px;
    }

    .empty-state {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 200px;
      color: rgba(0,0,0,0.54);
      font-style: italic;
    }

    .loading {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 400px;
    }
  `]
})
export class StoryBibleComponent implements OnInit {
  projectId = signal<string>('');
  bible = signal<StoryBible | undefined>(undefined);

  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private bibleService = inject(BibleService);

  ngOnInit(): void {
    const pId = this.route.snapshot.paramMap.get('id') || 
                this.route.parent?.snapshot.paramMap.get('id') || '';
    this.projectId.set(pId);
                     
    if (pId) {
      this.bibleService.getStoryBible(pId).subscribe({
        next: (data) => this.bible.set(data),
        error: (err) => console.error('Error loading bible', err)
      });
    }
  }

  goBack(): void {
    this.router.navigate(['/projects', this.projectId()]);
  }
}
