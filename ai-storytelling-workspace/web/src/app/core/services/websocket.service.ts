import { Injectable } from '@angular/core';
import { Subject, timer } from 'rxjs';
import { retry, tap } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

export interface WebSocketMessage {
  type: string;
  data?: any;
  timestamp?: string;
}

@Injectable({
  providedIn: 'root'
})
export class WebSocketService {
  private socket: WebSocket | null = null;
  private messagesSubject = new Subject<WebSocketMessage>();
  public messages$ = this.messagesSubject.asObservable();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  connect(projectId: string): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      return;
    }

    const wsUrl = `${environment.wsUrl}/ws/${projectId}`;
    console.log('WebSocket connecting to:', wsUrl);

    this.socket = new WebSocket(wsUrl);

    this.socket.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };

    this.socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        this.messagesSubject.next(message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.socket.onclose = () => {
      console.log('WebSocket disconnected');
      this.attemptReconnect(projectId);
    };
  }

  private attemptReconnect(projectId: string): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
      console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
      
      setTimeout(() => {
        this.connect(projectId);
      }, delay);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  send(message: WebSocketMessage): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
    }
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}
