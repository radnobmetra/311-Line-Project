import { Component, inject, signal, computed } from '@angular/core';
import { form, FormField } from '@angular/forms/signals';
import { FormsModule } from '@angular/forms'; // Permits the use of ngModel in the .html
import { RequestLog } from './../../interfaces/request-log';
import { RequestLogService } from '../../services/request-log.service';

// Needed for getting data from filter/sort options form
interface sortFilterInput {
    sortDate: string;
    filterStartDate: string;
    filterEndDate: string;
    filterTopic: string;
}

@Component({
    imports: [FormField, FormsModule],
    selector: 'app-requests',
    styleUrl: './requests.css',
    templateUrl: './requests.html',
})
export class Requests {
    // Inject the service to consume the data polling.
    requestsService = inject(RequestLogService);

    // Signal array to hold the raw request records.
    requests = signal<RequestLog[]>([]);

    // Will hold the search bar input.
    searchInput = signal<string>('');

    constructor() {
        this.requestsService.getAllServiceRequests().subscribe({
            next: (requests) => this.requests.set(requests),
            error: (err) => console.error("Request polling error:", err)
        });

        this.selectedMessages = [];
    }

    // Retrieves data from filter/sort options form
    sortFilterModel = signal<sortFilterInput>({
        sortDate: "",
        filterStartDate: "",
        filterEndDate: "",
        filterTopic: "",
    });
    sortFilterForm = form(this.sortFilterModel);

    // This function applies searching and filtering to the requests.
    displayed_reqs = computed(() => {
        // The "..." unpacks the signal array into a normal array so that it can be filtered and sorted.
        let processed_records = [...this.requests()];

        // If any of the fields are null, set them to an empty string so that
        // the search bar and filter functions don't throw errors.
        processed_records.forEach((record) => {
            if (record.requestId == null) record.requestId = "";
            if (record.phoneNumber == null) record.phoneNumber = "";
            if (record.topic == null) record.topic = "";
            if (record.createdAt == null) record.createdAt = "";
        });

        // Search Bar functionality
        const query = this.searchInput().toLowerCase().trim();
        if (query !== '') {
            processed_records = processed_records.filter(record => {
                if (
                record.requestId.toString().includes(query) ||
                record.phoneNumber.toLowerCase().includes(query) ||
                record.topic.toLowerCase().includes(query) ||
                record.createdAt.toLowerCase().includes(query)
                ) {
                    return true;
                } 
                else {
                    this.toggleSelectedMsg(record.id, true);
                    return false;
                }
            });
        }

        // Filter by topic
        const topicFilter = this.sortFilterForm.filterTopic().value();
        if (topicFilter) {
            processed_records = processed_records.filter(
                (record) => record.topic == topicFilter);
        }

        // Filter by end date (displays a record if its date is before an end date)
        const endDateFilter = this.sortFilterForm.filterEndDate().value();
        if (endDateFilter) {
            const end_date = Date.parse(endDateFilter);
            processed_records = processed_records.filter(
                (record) => Date.parse(record.createdAt) < end_date);
        }

        // Filter by start date (displays a record if its date is after a start date)
        const startDateFilter = this.sortFilterForm.filterStartDate().value();
        if (startDateFilter) {
            const start_date = Date.parse(startDateFilter);
            processed_records = processed_records.filter(
                (record) => Date.parse(record.createdAt) > start_date);
        }
        
        // Sort by date
        const sortDateOption = this.sortFilterForm.sortDate().value();
        if (sortDateOption) {
            // Sort by newest
            if (sortDateOption === "newest") {
                processed_records.sort(this.compare_dates_newest);
            }
            // Sort by oldest
            if (sortDateOption === "oldest") {
                processed_records.sort(this.compare_dates_oldest);
            }
        }

        return processed_records;
    });

    compare_dates_oldest(a: any, b: any) {
        //older dates are sorted after newer dates
        let a_int = Date.parse(a.createdAt);
        let b_int = Date.parse(b.createdAt);
        if (a_int > b_int) return 1;    //a is more recent -> sort a after b
        if (a_int < b_int) return -1;   //a is less recent -> sort a before b
        return 0;   //a == b -> return 0
    }

    compare_dates_newest(a: any, b: any) {
        //older dates are sorted after newer dates
        let a_int = Date.parse(a.createdAt);
        let b_int = Date.parse(b.createdAt);
        if (a_int < b_int) return 1;    //a is less recent -> sort a after b
        if (a_int > b_int) return -1;   //a is more recent -> sort a before b
        return 0;   //a == b -> return 0
    }

    // EXPORT TO CSV FUNCTIONALITY
    onExport(): void {
        let rows = this.displayed_reqs();

        if (this.selectedMessages) {
            if (this.selectedMessages.length > 0) {
                rows = rows.filter((record) => this.selectedMessages.indexOf(record.id) >= 0);
            }
        }

        // If there are no rows to export, log a warning and return early.
        if (!rows.length) {
            console.warn('No messages to export.');
            return;
        }

        // Converts the rows to CSV format and create a downloadable link.
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

    // Helper Functions
    // Flattens a nested object into a single-level object with dot-notation keys
    private flatten(obj: any, prefix = '', out: Record<string, any> = {}): Record<string, any> {
        for (const [key, value] of Object.entries(obj)) {
            const k = prefix ? `${prefix}.${key}` : key;
        
            const isPlainObject = value !== null &&
            typeof value === 'object' &&
            !Array.isArray(value) &&
            !(value instanceof Date) &&
            Object.keys(value as object).length > 0;

            if (isPlainObject) {
                this.flatten(value, k, out);
            } else {
                out[k] = value;
            }
        }
        return out;
    }

    // RFC 4180 cell escaping
    private cell(value: any): string {
        if (value === null || value === undefined) {
            return '';
        }
        let s = typeof value === 'object' ? JSON.stringify(value) : String(value);
        if (/[",\r\n]/.test(s)) {
            s = '"' + s.replace(/"/g, '""') + '"';
        }
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
                if (!seen.has(k)) { 
                    seen.add(k); headers.push(k);
                }
            }
        }
        // Create CSV lines
        const lines = [headers.map(h => this.cell(h)).join(',')];
        for (const row of flat) {
            lines.push(headers.map(h => this.cell(row[h])).join(','));
        }
        return lines.join('\r\n') + '\r\n';
    }
    
    // This array will hold the IDs of the messages that the user has selected to export.
    selectedMessages: string[];    

    toggleSelectedMsg(message_id: any, onlyRemoveMessage: boolean) {
    //this function updates the selectedMessages array when the user 
    //selects or unselects a message's checkbox.
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
        } else {
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

