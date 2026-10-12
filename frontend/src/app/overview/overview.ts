import { Sessions } from './../sessions/sessions';
import { Component, inject, signal} from '@angular/core';
import { Chart, registerables } from 'chart.js';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ServiceRequest } from '../../interfaces/service-request.interface';
import { ServiceRequestsService } from '../../services/service-requests.service';
import { Session } from '../../interfaces/session.interface';
import { SessionsService } from '../../services/sessions.service';

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

  // Same thing but for sessions
  sessionService = inject(SessionsService);
  sessionMap = new Map<string, number>();

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

    // Same as above but for sessions
    this.sessionService.getAllSessions().subscribe({
      next: (sessions) => {
        this.displayGraph(sessions);
      },
      error: (err) => console.error("Sessions polling error:", err)
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
    this.showTicketGraph([...this.serviceRequestsCountMap.keys()], [...this.serviceRequestsCountMap.values()]);
  }

  // Getting session data
  displayGraph(sessionsData: Session[]) {
    this.sessionMap.clear();
    sessionsData.forEach((session) => {
      var currCount = this.sessionMap.get(session.startedAt) ?? 0;
      this.sessionMap.set(session.startedAt, currCount+1);
    });

    // Extract all labels and count values from the hashmap into arrays and pass them to showGraph()
    this.showSessionGraph([...this.sessionMap.keys()], [...this.sessionMap.values()]);
  }

  // Function to display graphs with service-request status labels, along with their respective count.
  showTicketGraph(requestsStatusLabels: string[], statusCountData: number[]) {
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
        maintainAspectRatio: true,
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
        maintainAspectRatio: true,
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });

  }
  showSessionGraph(sessionLabels: string[], sessionDate: number[]) {
    // Destroy existing charts
    const existingChart3 = Chart.getChart("sessionChart");
    if (existingChart3) {
          existingChart3.destroy();
    }

    new Chart("sessionChart", {
        type: 'line',
        data: {
          labels: sessionLabels, /*This is label of each bar */
          datasets: [{
            label: 'Recent Sessions',  /*This is label of overall graph */
            data: sessionDate,
            borderWidth: 1
          }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  }
}
