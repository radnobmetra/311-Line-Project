
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Component, inject, signal } from '@angular/core';
import { DatePipe, DecimalPipe } from '@angular/common';

import { PhonePipe } from '../../pipes/phone.pipe';
import { SessionDetails } from '../../interfaces/session-details.interface';
import { Session } from '../../interfaces/session.interface';
import {
  SessionsService,
  SessionEvaluation
} from '../../services/sessions.service';
import { tableToCsv } from '../utils/exportToCSV';

@Component({
  selector: 'app-sessions',
  imports: [DatePipe, DecimalPipe, RouterLink, PhonePipe],
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

  /// Individual and combined evaluations, indexed by session ID.
  evaluations = signal<Record<string, SessionEvaluation | null>>({});

  // Selected outcome filter.
  currentFilter = signal<string>('ALL');

  // Loading states.
  loading = signal<boolean>(true);
  loadingOutcomes = signal<boolean>(false);

  // Error states.
  errorMessage = signal<string>('');
  outcomeError = signal<boolean>(false);

  constructor() {
    this.loadSessions();
  }

  // STEP 1: Retrieve session metadata.
  loadSessions(): void {

    this.loading.set(true);
    this.errorMessage.set('');
    this.outcomeError.set(false);
    this.evaluations.set({});

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

        // Only request outcomes if sessions exist.
        if (sessionsData.length > 0) {
          this.loadOutcomes();
        }
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

  // Retrieve individual and combined evaluation results
  // without blocking the session table.
  loadOutcomes(): void {

    this.loadingOutcomes.set(true);
    this.outcomeError.set(false);

    this.sessionsService.getSessionEvaluations(
      this.contactID || undefined
    ).subscribe({

      next: (evaluationData: Record<string, SessionEvaluation | null>) => {

        this.evaluations.set(evaluationData);
        this.loadingOutcomes.set(false);
      },

      error: (err: unknown) => {

        console.error('Error loading session evaluations:', err);

        this.outcomeError.set(true);
        this.loadingOutcomes.set(false);
      }

    });
  }

  // Update the selected outcome filter.
  setFilter(event: Event): void {

    const selectElement = event.target as HTMLSelectElement;

    this.currentFilter.set(selectElement.value);
  }

  // Get the combined final outcome for a session.
  getFinalOutcome(session: Session): string | null {
    return this.evaluations()[session.id]?.final_outcome ?? null;
  }

  // Get the individual AI evaluation score.
  getAiScore(session: Session): number | null {
    return this.evaluations()[session.id]?.ai_evaluation?.score ?? null;
  }

  // Get the stored user feedback summary.
  getUserFeedback(session: Session) {
    return this.evaluations()[session.id]?.user_feedback ?? null;
  }

  // Filter and sort the session table.
  get sortedSessions(): SessionDetails[] {

    const filter = this.currentFilter();

    const allSessions = Array.from(
      this.sessionMap().values()
    );

    const filteredSessions = allSessions.filter(item => {

      if (filter === 'ALL') {
        return true;
      }

      const outcome = this.getFinalOutcome(item.session);

      return outcome?.toUpperCase() === filter.toUpperCase();
    });

    return filteredSessions.sort(
      (a, b) => a.session.id.localeCompare(
        b.session.id,
        undefined,
        { numeric: true }
      )
    );
  }
}
