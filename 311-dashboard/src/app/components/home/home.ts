import { Component, OnInit} from '@angular/core';
import { Chart, registerables } from 'chart.js';
import { HomeService } from './home.service';

Chart.register(...registerables);

@Component({
  imports: [],
  selector: 'app-home',
  styleUrl: './home.css',
  templateUrl: './home.html',
})
export class Home implements OnInit {

  title = 'ticketData';

  data: any;
  dataStatus: any[] = [];
  dataCount: any[] =[];
  constructor(private _homeService: HomeService) {

  }


  ngOnInit() {
    this._homeService.showdata().subscribe(res => {

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
