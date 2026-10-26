import { ActivatedRoute, RouterLink } from '@angular/router';
import { Component, inject, signal, computed } from '@angular/core';
import { DatePipe } from '@angular/common';
import { ServiceRequestsService } from '../../services/service-requests.service';
import { ServiceRequest } from '../../interfaces/service-request.interface';
import { tableToCsv } from '../utils/exportToCSV';

@Component({
  imports: [RouterLink, DatePipe],
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
