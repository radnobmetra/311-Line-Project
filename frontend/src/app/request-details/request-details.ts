import { DatePipe } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ServiceRequest } from '../../interfaces/service-request.interface';
import { ServiceRequestsService } from '../../services/service-requests.service';

@Component({
  imports: [DatePipe],
  selector: 'app-request-details',
  styleUrl: './request-details.css',
  templateUrl: './request-details.html',
})
export class RequestDetails {
  requestId = inject(ActivatedRoute).snapshot.paramMap.get('id') ?? "";

  // Inject service.
  requestsService = inject(ServiceRequestsService);

  // Store the current request.
  request = signal<ServiceRequest | null>(null);

  constructor() {
    if (this.requestId) {
      this.requestsService.getRequestById(this.requestId).subscribe({
        next: (requestData) => {
          this.request.set(requestData);
        },
        error: (err) => {console.error('Error retrieving service request:', err);}
      });
    }
  }
}
