import { EventMessage } from './../../interfaces/events-db.interface';
import { Component, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { EventService } from './../../services/events.service';

// A custom data type for each row.
// interface Logs {
//   phoneNum: string;
//   id: string;
//   requestType: string;
// }

@Component({
  imports: [],
  selector: 'app-events',
  styleUrl: './events.css',
  templateUrl: './events.html',
})
export class Events {
  // Inject the messages service so we can consume the messages polling service.
  eventsService = inject(EventService);
  // Array that holds all messages.
  messages = signal<EventMessage[]>([]);

  constructor() {
    // New messages will be fetched here.
    // Must register takeUntilDestroyed() to unsubscribe when the component is destroyed to avoid
    // background memory leaks.
    this.eventsService.pollNewEvents().pipe(takeUntilDestroyed()).subscribe({
      next: (messages) => this.messages.set(messages),
      error: (err) => console.error("Messages polling error:", err)
    });
  }
  onExport(): void {
    // TODO: wire up real export logic (CSV, JSON, PDF, etc.)
    console.log('Export clicked');
  }
}

