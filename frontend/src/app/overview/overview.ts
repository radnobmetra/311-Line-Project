import { Component, OnInit} from '@angular/core';
import { Chart, registerables } from 'chart.js';
import { OverviewService } from './overview.service';

Chart.register(...registerables);

@Component({
  imports: [],
  selector: 'app-overview',
  styleUrl: './overview.css',
  templateUrl: './overview.html',
})
export class Overview implements OnInit {

  title = 'ticketData';

  data: any;
  dataStatus: any[] = [];
  dataCount: any[] =[];
  constructor(private _overviewService: OverviewService) {

  }


  ngOnInit() {
    this._overviewService.showdata().subscribe(res => {

      this.data = res;

      if (this.data != null) {
        for (let i = 0; i < this.data.length; i++) {
          this.dataStatus.push(this.data[i].status);
          this.dataCount.push(this.data[i].count);
        }
      }
      console.log(this.dataCount)
      this.showGraph(this.dataStatus, this.dataCount);

    }); 

  }

  
  showGraph(dataStatus: any, dataCount: any) {
    new Chart("ticketChart", {
      type: 'bar',
      data: {
        labels: dataStatus, /*This is label of each bar */
        datasets: [{
          label: 'Ticket Count',  /*This is label of overall graph */
          data: dataCount,
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
        labels: dataStatus, /*This is label of each bar */
        datasets: [{
          label: 'Ticket Count',  /*This is label of overall graph */
          data: dataCount,
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
