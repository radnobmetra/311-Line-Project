import { Component } from '@angular/core';
import {recordsTable} from '../sort-filter-tool/sortedFilteredTable.js';

@Component({
  imports: [recordsTable],
  selector: 'app-requests',
  styleUrl: './requests.css',
  templateUrl: './requests.html',
})
export class Requests {}
