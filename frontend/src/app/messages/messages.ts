
import { Component, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { ActivatedRoute } from '@angular/router';

import { SessionsService } from '../../services/sessions.service';
import { Session } from '../../interfaces/session.interface';
import { tableToCsv } from '../utils/exportToCSV';

// Structure of an event returned by our Flask API.
interface SessionEvent {
  author?: string;
  timestamp?: string | null;
  content?: {
    parts?: {
      text?: string | null;
    }[];
  };
}

// The session API returns metadata plus events.
interface SessionWithEvents extends Session {
  events?: SessionEvent[];
}

// Structure used to display each log entry.
interface LogEntry {
  id: number;
  author: string;
  body: string;
  timestamp: string | null;
  type: string;
}

@Component({
  selector: 'app-messages',
  imports: [DatePipe],
  templateUrl: './messages.html',
  styleUrl: './messages.css'
})
export class Messages {

  private route = inject(ActivatedRoute);
  private sessionsService = inject(SessionsService);

  onExport(): void {
    tableToCsv(this.logEntries(), 'messages');
  }
  // The session ID is on the parent route:
  // /session-details/:id/messages
  sessionID =
    this.route.parent?.snapshot.paramMap.get('id') ??
    this.route.snapshot.paramMap.get('id') ??
    '';

  // Session log entries.
  logEntries = signal<LogEntry[]>([]);

  // Loading and error states.
  loading = signal<boolean>(true);
  errorMessage = signal<string>('');

  constructor() {
    this.loadSessionLog();
  }

  loadSessionLog(): void {

    if (!this.sessionID) {
      this.loading.set(false);
      this.errorMessage.set(
        'Select a session from the Sessions page to view its log.'
      );
      return;
    }

    this.loading.set(true);
    this.errorMessage.set('');

    // Retrieve the full session and its events from Flask.
    this.sessionsService.getSessionById(this.sessionID).subscribe({

      next: (session: Session) => {

        const sessionData = session as SessionWithEvents;
        const events = sessionData.events ?? [];

        const entries: LogEntry[] = [];

        // Convert Google Agent Engine events into log entries.
        events.forEach((event, index) => {

          const body = (event.content?.parts ?? [])
            .map(part => part.text ?? '')
            .filter(text => text.trim().length > 0)
            .join('\n\n');

          // Skip events without readable text.
          if (!body.trim()) {
            return;
          }

          const author = event.author ?? 'Unknown';

          entries.push({
            id: index,
            author: author,
            body: this.formatEventText(body),
            timestamp: event.timestamp ?? null,
            type: author.toLowerCase() === 'user'
              ? 'user'
              : author.toLowerCase() === 'system'
                ? 'system'
                : 'agent'
          });
        });

        this.logEntries.set(entries);
        this.loading.set(false);
      },

      error: (err: unknown) => {
        console.error('Error retrieving session log:', err);

        this.errorMessage.set(
          'Unable to load this session log. Check the Flask backend.'
        );

        this.loading.set(false);
      }

    });
  }

  // Format saved outcome events for easier reading.
  formatEventText(text: string): string {

    try {
      const data = JSON.parse(text);

      if (
        data &&
        typeof data === 'object' &&
        typeof data.final_outcome === 'string'
      ) {
        return `Final outcome: ${data.final_outcome}`;
      }

    } catch {
      // Normal text messages are not JSON.
    }

    return text;
  }
}
