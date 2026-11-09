import { FormsModule } from '@angular/forms'; // Permits the use of ngModel in the .html

import { ActivatedRoute, RouterLink } from '@angular/router';
import { Component, inject, signal, computed } from '@angular/core';
import { DatePipe } from '@angular/common';
import { ServiceRequestsService } from '../../services/service-requests.service';
import { ServiceRequest } from '../../interfaces/service-request.interface';
import { tableToCsv } from '../utils/exportToCSV';

@Component({
  imports: [RouterLink, DatePipe, FormsModule],
  selector: 'app-service-requests',
  styleUrl: './service-requests.css',
  templateUrl: './service-requests.html',
})
export class ServiceRequests {
  sessionID = inject(ActivatedRoute).snapshot.paramMap.get('id') ?? "";

  // Inject the service requests service to fetch service requests from the db.
  serviceRequestsService = inject(ServiceRequestsService);

  // Array to store all available service requests
  serviceRequests = signal<ServiceRequest[]>([]);

  // Will hold the search bar input.
  searchInput = signal<string>('');

  constructor() {
    // Fetch all service requests when the component is initialized.
    // If a session ID is provided, fetch service requests for that session; otherwise, fetch all service requests.
    if (this.sessionID) {
      this.serviceRequestsService.getAllServiceRequestsBySessionId(this.sessionID).subscribe({
        next: (serviceRequests) => this.serviceRequests.set(serviceRequests),
        error: (err) => console.error("Service requests polling error:", err)
      });
    } else{
      this.serviceRequestsService.getAllServiceRequests().subscribe({
        next: (serviceRequests) => this.serviceRequests.set(serviceRequests),
        error: (err) => console.error("Service requests polling error:", err)
      });
    }
  }

  // This function applies searching to the service requests table.
  // It works the same way as the search bars on the requests and sessions
  // pages: the query is case-insensitive and trimmed, and it is matched
  // against the values displayed in the table.
  displayed_reqs = computed(() => {
    const query = this.searchInput().toLowerCase().trim();

    return this.serviceRequests().filter((record) => {

      // An empty search box shows every record.
      if (query === '') {
        return true;
      }

      // Null safe comparisons so the search bar doesn't throw errors.
      return (
        String(record.id ?? '').toLowerCase().includes(query) ||
        String(record.title ?? '').toLowerCase().includes(query) ||
        String(record.status ?? '').toLowerCase().includes(query) ||
        String(record.createdAt ?? '').toLowerCase().includes(query)
      );
    });
  });

  onExport(): void {
    let rows = this.serviceRequests();
    // Calls the export utility.
    tableToCsv(rows, 'service-requests');
  }
  contactRequests = computed(() => {
    return this.serviceRequests().filter(request => request.sessionId === this.sessionID);
  });
  onExportContact(): void {
    tableToCsv(this.contactRequests(), `service-requests-${this.sessionID}`);
  }
}
