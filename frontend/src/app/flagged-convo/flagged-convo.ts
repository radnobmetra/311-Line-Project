import { Component, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { PhonePipe } from '../../pipes/phone.pipe';
import { Flagged } from '../../interfaces/flagged-convo.interface';
import { FlaggedService } from '../../services/flagged-convo.service'
import { tableToCsv } from '../utils/exportToCSV';


@Component({
  imports: [DatePipe, RouterLink, PhonePipe],
  selector: 'app-flagged-convo',
  styleUrl: './flagged-convo.css',
  templateUrl: './flagged-convo.html',
})
export class FlaggedConvo { 
  // inject the flagged convo service to get flagged markers from db
  flaggedService = inject(FlaggedService);

  // store all flagged convos in array
  flagged = signal<Flagged[]>([]);

  constructor() {
    //get all flagged convos from db
    this.flaggedService.getAllConvos().subscribe ({
      next: (convoData) => {this.flagged.set(convoData);},
      error: (err) => console.error("Error fetching data:", err)
    })
  }

  onExport(): void {
    let rows = this.flagged();
    // Calls the export utility.
    tableToCsv(rows, 'flagged-convos');
  }
}
