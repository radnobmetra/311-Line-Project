import { Component, input } from '@angular/core';

@Component({
  imports: [],
  selector: 'app-chart-wrapper',
  styleUrl: './chart-wrapper.css',
  templateUrl: './chart-wrapper.html',
})
export class ChartWrapper {
    loading = input(false);
    error = input('');
}
