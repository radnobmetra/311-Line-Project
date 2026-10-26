import { Sessions } from './../sessions/sessions';
import { Component, inject, signal } from '@angular/core';
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

  // signals for time range selections
  periodRange = signal<'year'|'month'|'week'|'day'|'hour'>('day')
  rangeUnit = signal<number>(7); //defaults to 7 days

  storedSessions: Session[] = [];

  //making slider available for only period: day, week, and month
  get isSliderAvailable(): boolean {
    const p = this.periodRange();
    return p==='day'|| p==='week' || p==='month';
  }

  //alters slider options based on period
  get sliderMax(): number {
    switch (this.periodRange()) {
      case 'week': return 52;
      case 'month': return 12;
      case 'day': default: return 7;
    }
  }

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
        this.storedSessions = sessions; // saves data to class variable storedSessions
        this.displayGraph(sessions, this.periodRange(), this.rangeUnit()); // saves choice of which time range to show
      },
      error: (err) => console.error("Sessions polling error:", err)
    });

  }

  // Function to get current requests statuses and their counts from service requests data.
  displayCharts(requestsData: ServiceRequest[]) {
    // Clear out the hashmap of service requests.
    this.serviceRequestsCountMap.clear();
    // Iterate through the service requests and update the hashmap <status label, count>
    requestsData.forEach((serviceRequest) => {
      // Get the current count of the service-request status label. If not defined, set it to 0;
      const currCount = this.serviceRequestsCountMap.get(serviceRequest.status) ?? 0;
      // Increase the status label value by 1.
      this.serviceRequestsCountMap.set(serviceRequest.status, currCount + 1);
    });

    // Extract all labels and count values from the hashmap into arrays and pass them to showGraph()
    this.showTicketGraph([...this.serviceRequestsCountMap.keys()], [...this.serviceRequestsCountMap.values()]);
  }


  // Getting session data 
  // convert time format in here
  displayGraph(sessionsData: Session[], period: 'hour'|'day'|'week'|'month'|'year', range: number) { // need to make buttons for each period
    this.sessionMap.clear();

    const now = new Date().getTime();
    let cutoff = 0;

    //need to change so it starts at 12 am - 12 pm
    if (period === 'hour') {
      cutoff = now - (24 * 60 * 60 * 1000); // 24 * 1 Hour fixed to 24 hours when on hour //fix to start at 12 - 12 
    } else if (period === 'day') {
      cutoff = now - (range * 24 * 60 * 60 * 1000); // Range * 1 Day
    } else if (period === 'month') {
      cutoff = now - (range * 30 * 24 * 60 * 60 * 1000); // Range * 30 Days
    } else if (period === 'year') {
      cutoff = now - (365 * 365 * 24 * 60 * 60 * 1000); // 3 * 365 Days (fix time to 3 years max)
    }

    //filters json data to only get the date for x axis
    const filteredSessions = sessionsData.filter((session) => {
      const sessionTime = new Date(session.startedAt).getTime();
      return sessionTime >= cutoff;
    })

    filteredSessions.forEach((session) => {
      const newDate = this.formatDate(session.startedAt, period);
      var currCount = this.sessionMap.get(newDate) ?? 0;
      this.sessionMap.set(newDate, currCount + 1);
      })


    const sortedEntries = [...this.sessionMap.entries()].sort((a, b) => a[0].localeCompare(b[0]));
    const sortedLabels = sortedEntries.map(entry => entry[0]);
    const sortedData = sortedEntries.map(entry => entry[1]);

    // Extract all labels and count values from the hashmap into arrays and pass them to showGraph()
    this.showSessionGraph(sortedLabels, sortedData);
  }

  //changes date format to YYYY-MM-DD
  private formatDate(dateString: string, period: 'hour'|'day'|'week'|'month'|'year'): string {
    if (!dateString) 
      return '';

    switch (period) {
      case 'hour':
        return dateString.substring(11,13)
      case 'year':
        return dateString.substring(0,4);
      case 'month':
        return dateString.substring(0,7);
      case 'day':
      default:
        return dateString.substring(0,10);
    }
  }

  //changes periodRange based on option clicked
  periodToggle(newPeriod: 'hour'|'day'|'week'|'month'|'year') {
    this.periodRange.set(newPeriod);

    // set a default time range when selecting day, week, and month
    if (newPeriod === 'day') this.rangeUnit.set(7);
    else if (newPeriod === 'week') this.rangeUnit.set(4);
    else if (newPeriod === 'month') this.rangeUnit.set(12);

    this.displayGraph(this.storedSessions, this.periodRange(), this.rangeUnit()); 
  }

  //changs time range based on where user puts slider
  onSliderChange(event: Event) {
    const val = parseInt((event.target as HTMLInputElement).value, 10);
    this.rangeUnit.set(val);
    this.displayGraph(this.storedSessions, this.periodRange(), this.rangeUnit());
  }

  // Function to display graphs with service-request status labels, along with their respective count.
  showTicketGraph(requestsStatusLabels: string[], statusCountData: number[]) {
    // Destroy existing charts
    const existingChart = Chart.getChart("ticketChart");

    if (existingChart) {
      existingChart.destroy();
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
            beginAtZero: true,
            ticks: {
              precision: 0,
            }
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
            beginAtZero: true,
            ticks: {
              precision: 0, //makes tick values whole numbers
            }
          }
        }
      }
    });
  }
}
