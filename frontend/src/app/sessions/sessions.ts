
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Component, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';

import { PhonePipe } from '../../pipes/phone.pipe';
import { SessionDetails } from '../../interfaces/session-details.interface';
import { Session } from '../../interfaces/session.interface';
import { SessionsService } from '../../services/sessions.service';
import { tableToCsv } from '../utils/exportToCSV';

@Component({
  selector: 'app-sessions',
  imports: [DatePipe, RouterLink, PhonePipe],
  templateUrl: './sessions.html',
  styleUrl: './sessions.css'
})
export class Sessions {

  onExport(): void {
    const rows = Array.from(this.sessionMap().values())
      .map(item => item.session);

    tableToCsv(
      rows,
      this.contactID ? `sessions-${this.contactID}` : 'sessions'
    );
  }

  // Get the contact ID from the URL, if one exists.
  contactID = inject(ActivatedRoute).snapshot.paramMap.get('id') ?? '';

  // Backend service.
  sessionsService = inject(SessionsService);

  // Session data.
  sessionMap = signal<Map<string, SessionDetails>>(new Map());


  // Session loading and error states.
  loading = signal<boolean>(true);
  errorMessage = signal<string>('');

  constructor() {
    this.loadSessions();
  }

  // STEP 1: Retrieve session metadata.
  loadSessions(): void {

    this.loading.set(true);
    this.errorMessage.set('');

    const request = this.contactID
      ? this.sessionsService.getSessionsPerContact(this.contactID)
      : this.sessionsService.getAllSessions();

    request.subscribe({

      next: (sessionsData: Session[]) => {

        const map = new Map<string, SessionDetails>();

        for (const session of sessionsData) {
          map.set(session.id, {
            session: session,
            phoneNumber: session.contactId
          });
        }

        // Display sessions immediately.
        this.sessionMap.set(map);
        this.loading.set(false);

      },

      error: (err: unknown) => {

        console.error('Error loading sessions:', err);

        this.errorMessage.set(
          'Unable to load sessions. Check that the Flask backend is running.'
        );

        this.loading.set(false);
      }

    });
  }

  // Sort sessions by ID.
  get sortedSessions(): SessionDetails[] {

    const allSessions = Array.from(
      this.sessionMap().values()
    );

    return allSessions.sort(
      (a, b) => a.session.id.localeCompare(
        b.session.id,
        undefined,
        { numeric: true }
      )
    );
  }
}
