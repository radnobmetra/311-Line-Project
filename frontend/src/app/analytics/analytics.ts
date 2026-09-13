import { Component, computed, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

// A custom data type for each row.
interface Logs {
  phoneNum: string;
  id: string;
  requestType: string;
}

@Component({
  imports: [FormsModule, CommonModule],
  selector: 'app-analytics',
  styleUrl: './analytics.css',
  templateUrl: './analytics.html',
})
export class Analytics {
  // Example rows. Will be replaced with actual data from the backend later.
  logs = signal<Logs[]>([
    { phoneNum: '123-456-7890', id: '10001', requestType: 'Request A' },
    { phoneNum: '987-654-3210', id: '10002', requestType: 'Request B' },
    { phoneNum: '555-555-5555', id: '10003', requestType: 'Request C' }
  ]);

  searchInput = signal<string>('');

  filteredLogs = computed(() => {
    const searchTerm = this.searchInput().toLowerCase();

    // If the search is empty, return all logs.
    if (!searchTerm) {
      return this.logs();
    }

    // Returns only the logs that match the search term in any of the three columns.
    return this.logs().filter(log =>
      log.phoneNum.toLowerCase().includes(searchTerm) ||
      log.id.toLowerCase().includes(searchTerm) ||
      log.requestType.toLowerCase().includes(searchTerm)
    );
  })
}
