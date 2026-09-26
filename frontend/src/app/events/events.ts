import { EventMessage } from './../../interfaces/events-db.interface';
import { Component, inject, signal, computed } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { EventService } from './../../services/events.service';
import { form, FormField } from '@angular/forms/signals';
import { FormsModule } from '@angular/forms';

// A custom data type for each row.
// interface Logs {
//   phoneNum: string;
//   id: string;
//   requestType: string;
// }

//needed for getting data from filter/sort options form
interface sortFilterInput {
  //sortDate: string;
  //filterStartDate: string;
  //filterEndDate: string;
  //filterTopic: string;
  filterStatus: string;
  filterOutcome: string;
}

@Component({
  imports: [FormField, FormsModule],
  selector: 'app-events',
  styleUrl: './events.css',
  templateUrl: './events.html',
})

export class Events {
  // Inject the messages service so we can consume the messages polling service.
  eventsService = inject(EventService);
  // Array that holds all messages.
  messages = signal<EventMessage[]>([]);

  //needed for getting data from filter/sort options form
  sortFilterModel = signal<sortFilterInput>({
    //sortDate: "",
    //filterStartDate: "",
    //filterEndDate: "",
    //filterTopic: "",
    filterStatus: "", 
    filterOutcome: "",
  });
  sortFilterForm = form(this.sortFilterModel);
    
  constructor() {
    // New messages will be fetched here.
    // Must register takeUntilDestroyed() to unsubscribe when the component is destroyed to avoid
    // background memory leaks.
    this.eventsService.pollNewEvents().pipe(takeUntilDestroyed()).subscribe({
      next: (messages) => this.messages.set(messages),
      error: (err) => console.error("Messages polling error:", err)
    });

    this.selectedMessages = [];
  }


  //==============================================
  //              exporting to csv 
  //==============================================

  onExport(): void {
    let rows = this.displayedMessages();

    //if messages have been selected, only export the messages that have
    //been selected
    if (this.selectedMessages) {
      if (this.selectedMessages.length > 0) {
        rows = rows.filter((record) => this.selectedMessages.indexOf(record.id) >= 0);
      }
    }

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

  //==============================================
  //        signal for sorted/filtered data
  //==============================================

  displayedMessages = computed(() => {
    //sortMessages() applies searching and filtering to messages.
    return this.sortMessages();     
  });

  //==============================================
  //            signal for search bar
  //==============================================

    searchInput = signal<string>('');

  //==============================================
  //       record sorting/filtering options
  //==============================================

  private sortMessages(): any[] {
    let tempArr = this.messages();

    //filter by status
    if (this.sortFilterForm.filterStatus().value()) {
      tempArr = tempArr.filter(
        (record) => {
          if (!(record.status == this.sortFilterForm.filterStatus().value())) {
            //if record is filtered out, deselect it to avoid errors
            this.toggleSelectedMsg(record.id, true);
            return false;
          }
          else return true;
        });
    }

    //filter by outcome
    if (this.sortFilterForm.filterOutcome().value()) {
      tempArr = tempArr.filter(
        (record) => {
          if (!(record.outcome == this.sortFilterForm.filterOutcome().value())) {
            //if record is filtered out, deselect it to avoid errors
            this.toggleSelectedMsg(record.id, true);
            return false;
          }
          else return true;
        });
    }

    const searchTerm = this.searchInput().toLowerCase();

    //search bar
    if (searchTerm) {
      tempArr = tempArr.filter(
        (record) => {
          if (!(record.status.toLowerCase().includes(searchTerm) ||
            record.user_id.toLowerCase().includes(searchTerm) ||
            record.outcome.toLowerCase().includes(searchTerm))) {
            //if record is filtered out, deselect it to avoid errors
            this.toggleSelectedMsg(record.id, true);
            return false;
          }
          else return true;
        });
    }

    return tempArr;
  }

  //==============================================
  //       selecting messages to export
  //==============================================

  selectedMessages: string[];    //array of elements that are selected to be exported.

  toggleSelectedMsg(message_id: any, onlyRemoveMessage: boolean) {
    //this function updates the selectedMessages array when the user 
    // selects or unselects a message's checkbox.
    //if onlyRemoveMessage = true, the function will deselect the message 
    //if it's selected, and it will not select the message if it's not selected.

    if (this.selectedMessages.length > 0) {
      let msg_id_index = this.selectedMessages.indexOf(message_id);
      //if message_id is in array of selected elements, remove it 
      // from array to unselect it
      if (msg_id_index != -1) {
        this.selectedMessages.splice(msg_id_index, 1);
      } 
      //if ID isn't in array of selected elements, add it to array
      else if (onlyRemoveMessage == false) {
        this.selectedMessages.push(message_id);
      }
    }
    else {
      //create selectedMessages array if its not initialized
    if (!this.selectedMessages) {
      this.selectedMessages = [];
    }
    //add id to array if array is empty
    if (this.selectedMessages.length == 0 && onlyRemoveMessage == false) {
      this.selectedMessages.push(message_id);
    }
    }
  }
}

