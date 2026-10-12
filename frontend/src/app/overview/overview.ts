import { Component, inject, signal} from '@angular/core';
import { Chart, registerables } from 'chart.js';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ServiceRequest } from '../../interfaces/service-request.interface';
import { ServiceRequestsService } from '../../services/service-requests.service';

Chart.register(...registerables);

@Component({
  imports: [],
  selector: 'app-overview',
  styleUrl: './overview.css',
  templateUrl: './overview.html',
})
export class Overview {
  // Inject the ServiceRequest service so we can consume it 
  serviceRequestsService = inject(ServiceRequestsService);
  // Hashmap that will store requests' statuses and their respective count. 
  serviceRequestsCountMap = new Map<string, number>();

  constructor() {
    // New requests will be fetched here.
    // Must register takeUntilDestroyed() to unsubscribe when the component is destroyed to avoid
    // background memory leaks.
    this.serviceRequestsService.getAllServiceRequests().subscribe({
      next: (serviceRequests) => {
        this.displayCharts(serviceRequests);
      },
      error: (err) => console.error("Service Requests polling error:", err)
    });
  }

  // Function to get current requests statuses and their counts from service requests data.
  displayCharts(requestsData: ServiceRequest[])
  {
    // Clear out the hashmap of service requests.
    this.serviceRequestsCountMap.clear();
    // Iterate through the service requests and update the hashmap <status label, count>
    requestsData.forEach((serviceRequest) => {
      // Get the current count of the service-request status label. If not defined, set it to 0;
      const currCount = this.serviceRequestsCountMap.get(serviceRequest.status) ?? 0;
      // Increase the status label value by 1.
      this.serviceRequestsCountMap.set(serviceRequest.status, currCount+1);
    });

    // Extract all labels and count values from the hashmap into arrays and pass them to showGraph()
    this.showGraph([...this.serviceRequestsCountMap.keys()], [...this.serviceRequestsCountMap.values()]);
  }
  
  // Function to display graphs with service-request status labels, along with their respective count. 
  showGraph(requestsStatusLabels: string[], statusCountData: number[])
  {
    // Destroy existing charts
    const existingChart = Chart.getChart("ticketChart"); 
    const existingChart2 = Chart.getChart("ticketChart2"); 
    if (existingChart) {
          existingChart.destroy();
    }
    if (existingChart2) {
          existingChart2.destroy();
    }

    // Create new charts
    new Chart("ticketChart", {
        type: 'bar',
        data: {
          labels: requestsStatusLabels, /*This is label of each bar */
          datasets: [{
            label: 'Ticket Count',  /*This is label of overall graph */
            data: statusCountData,
            borderWidth: 1
          }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  
    new Chart("ticketChart2", {
        type: 'bar',
        data: {
          labels: requestsStatusLabels, /*This is label of each bar */
          datasets: [{
            label: 'Ticket Count',  /*This is label of overall graph */
            data: statusCountData,
            borderWidth: 1
          }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  }
}
