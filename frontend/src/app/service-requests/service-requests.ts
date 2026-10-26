import { FormsModule } from '@angular/forms'; // Permits the use of ngModel in the .html
import { form, FormField } from '@angular/forms/signals';

import { ActivatedRoute, RouterLink } from '@angular/router';
import { Component, inject, signal, computed } from '@angular/core';
import { DatePipe } from '@angular/common';
import { ServiceRequestsService } from '../../services/service-requests.service';
import { ServiceRequest } from '../../interfaces/service-request.interface';
import { tableToCsv } from '../utils/exportToCSV';

interface sortFilterInput {
    sortDate: string;
    filterStartDate: string;
    filterEndDate: string;
    filterTopic: string;
}

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
        let processed_records = [...this.serviceRequests()];

        // If any of the fields are null, set them to an empty string so that
        // the search bar and filter functions don't throw errors.
        processed_records.forEach((record) => {
            if (record.id == null) record.id = "";
        });

        // Search Bar functionality
        const query = this.searchInput().toLowerCase().trim();
        if (query !== '') {
            processed_records = processed_records.filter(record => {
                if (
                record.id.toString().includes(query)
                ) {
                    return true;
                }
                else {
                    // this.toggleSelectedMsg(record.id, true);
                    return false;
                }
            });
        }

        // Filter by id
        const idFilter = this.sortFilterForm.filterTopic().value();
        if (idFilter) {
            processed_records = processed_records.filter(
                (record) => record.id == idFilter);
        }

        return processed_records;
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
