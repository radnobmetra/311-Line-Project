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
    const rows = this.messages();
    if (!rows.length) {
      console.warn('No messages to export.');
      return;
    }

    const csv = this.toCsv(rows);
    const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);

    const stamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-');
    const a = document.createElement('a');
    a.href = url;
    a.download = `events-db-${stamp}.csv`;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

// helper functions

  // Flatten nested objects into dotted keys, e.g. { actor: { id: 1 } } -> "actor.id"
  private flatten(obj: any, prefix = '', out: Record<string, any> = {}): Record<string, any> {
    for (const [key, value] of Object.entries(obj)) {
      const k = prefix ? `${prefix}.${key}` : key;
      const isPlainObject =
        value !== null &&
        typeof value === 'object' &&
        !Array.isArray(value) &&
        !(value instanceof Date) &&
        Object.keys(value as object).length > 0;

      if (isPlainObject) this.flatten(value, k, out);
      else out[k] = value;
    }
    return out;
  }

  // RFC 4180 cell escaping
  private cell(value: any): string {
    if (value === null || value === undefined) return '';
    let s = typeof value === 'object' ? JSON.stringify(value) : String(value);
    if (/[",\r\n]/.test(s)) s = '"' + s.replace(/"/g, '""') + '"';
    return s;
  }

  // Converts to the CSV
  private toCsv(rows: any[]): string {
    const flat = rows.map(r => this.flatten(r));

    // Union of all keys, preserving first-seen order
    const headers: string[] = [];
    const seen = new Set<string>();
    for (const row of flat) {
      for (const k of Object.keys(row)) {
        if (!seen.has(k)) { seen.add(k); headers.push(k); }
      }
    }

    const lines = [headers.map(h => this.cell(h)).join(',')];
    for (const row of flat) {
      lines.push(headers.map(h => this.cell(row[h])).join(','));
    }
    return lines.join('\r\n') + '\r\n';
  }

}

