import { Sessions } from './../sessions/sessions';
import { Component, inject, Signal, signal } from '@angular/core';
import { Chart, registerables } from 'chart.js';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ServiceRequest } from '../../interfaces/service-request.interface';
import { ServiceRequestsService } from '../../services/service-requests.service';
import { Session } from '../../interfaces/session.interface';
import { SessionsService } from '../../services/sessions.service';
import { ChartWrapper } from '../chart-wrapper/chart-wrapper';

Chart.register(...registerables);

@Component({
  imports: [ChartWrapper],
  selector: 'app-overview',
  styleUrl: './overview.css',
  templateUrl: './overview.html',
})
export class Overview {
  // Hashmap that will store session outcomes and their respective count.
  sessionOutcomesCountMap = new Map<string, number>();

  // Same thing but for sessions
  sessionService = inject(SessionsService);
  sessionMap = new Map<string, number>();

  // signals for time range selections
  periodRange = signal<'year'|'month'|'week'|'day'|'hour'>('day')
  rangeUnit = signal<number>(7); //defaults to 7 days

  storedSessions: Session[] = [];
  sessionsCount = signal<number>(0);

  sessionOutcomesLoading = signal(true);
  sessionOutcomesError = signal('');

  sessionsLoading = signal(true);
  sessionsError = signal('');

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
    this.sessionOutcomesLoading.set(true);
    this.sessionOutcomesError.set('');

    this.sessionsLoading.set(true);
    this.sessionsError.set('');

    // Fetch all sesssions outcomes.
    // Must register takeUntilDestroyed() to unsubscribe when the component is destroyed to avoid
    // background memory leaks.
    this.sessionService.getSessionOutcomes().subscribe({
      next: (sessionsOutcomes) => {
        this.displayCharts(sessionsOutcomes);

        this.sessionOutcomesLoading.set(false);
      },
      error: (err) => {
        console.error("Session outcomes fetching error:", err);
        this.sessionOutcomesError.set("Unable to load chart.");
        this.sessionOutcomesLoading.set(false);
      }
    });

    // Same as above but for sessions
    this.sessionService.getAllSessions().subscribe({
      next: (sessions) => {
        this.storedSessions = sessions; // saves data to class variable storedSessions
        this.sessionsCount.set(sessions.length); // Set sessions count
        this.displayGraph(sessions, this.periodRange(), this.rangeUnit()); // saves choice of which time range to show

        this.sessionsLoading.set(false);
      },
      error: (err) => {
        console.error("Sessions fetching error:", err);
        this.sessionsError.set("Unable to load chart.");
        this.sessionsLoading.set(false);
      }
    });

  }

  // Function to get session outcomes and their counts.
  displayCharts(outcomesData: Record<string, string | null>) {
    // Clear out the hashmap.
    this.sessionOutcomesCountMap.clear();
    // Iterate through the outcomes and update the hashmap <label, count>
    for (const outcome of Object.values(outcomesData))
    {
      // Get the current count of the outcome label. If not defined, set it to 0;
      const currCount = this.sessionOutcomesCountMap.get(outcome ?? "UNDEFINED") ?? 0;
      // Increase the count by 1.
      this.sessionOutcomesCountMap.set(outcome ?? "UNDEFINED", currCount + 1);
    }

    // Extract all labels and count values from the hashmap into arrays and pass them to showGraph()
    this.showSessionOutcomesGraph([...this.sessionOutcomesCountMap.keys()], [...this.sessionOutcomesCountMap.values()]);
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
  showSessionOutcomesGraph(sessionOutcomesLabels: string[], outcomesCountData: number[]) {
    // Destroy existing charts
    const existingChart = Chart.getChart("sessionsOutcomeChart");

    if (existingChart) {
      existingChart.destroy();
    }

    // Create new charts
    new Chart("sessionsOutcomeChart", {
      type: 'bar',
      data: {
        labels: sessionOutcomesLabels, /*This is label of each bar */
        datasets: [{
          label: 'Sessions Count',  /*This is label of overall graph */
          data: outcomesCountData,
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
