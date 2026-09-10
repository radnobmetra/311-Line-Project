import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import {recordsTable} from './sortedFilteredTable.js';

@Component({
  imports: [RouterOutlet, recordsTable],
  selector: 'app-root',
  styleUrl: './app.css',
  templateUrl: './app.html',
})
export class App {
  protected readonly title = signal('my-app');
}
