
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, switchMap, map } from 'rxjs';
import { Session } from '../interfaces/session.interface';
import { Contact } from '../interfaces/contact.interface';
import { environment } from '../environments/environment';

export interface SessionEvaluation {
  ai_evaluation: {
    score: number;
  } | null;

  user_feedback: {
    thumbs_up: number;
    thumbs_down: number;
    rating: string | null;
  } | null;

  final_outcome: 'HELPED' | 'NOT_HELPED' | 'UNCLEAR' | null;
}

@Injectable({
  providedIn: 'root'
})
export class SessionsService {

  private http = inject(HttpClient);

  // Flask backend endpoints.
  apiUrl = `${environment.apiUrl}/sessions`;
  contactsApiUrl = `${environment.apiUrl}/contacts`;

  // Retrieve all sessions (metadata only).
  getAllSessions(): Observable<Session[]> {
    return this.http.get<Session[]>(this.apiUrl);
  }

  // Retrieve a specific session with its events.
  getSessionById(sessionId: string): Observable<Session> {
    return this.http.get<Session>(
      `${this.apiUrl}/${encodeURIComponent(sessionId)}`
    );
  }

  // Retrieve sessions belonging to a contact.
  getSessionsPerContact(contactId: string): Observable<Session[]> {
    return this.http.get<Session[]>(
      this.apiUrl,
      {
        params: { contactId }
      }
    );
  }

  // Retrieve evaluation outcomes separately.
  getSessionOutcomes(
    contactId?: string
  ): Observable<Record<string, string | null>> {
    return this.http.get<Record<string, string | null>>(
      `${this.apiUrl}/outcomes`,
      {
        params: contactId ? { contactId } : {}
      }
    );
  }
  // Retrieve the individual AI evaluation, user feedback,
  // and combined final outcome for each session.
  getSessionEvaluations(
    contactId?: string
  ): Observable<Record<string, SessionEvaluation | null>> {
    return this.http.get<Record<string, SessionEvaluation | null>>(
      `${this.apiUrl}/evaluations`,
      {
        params: contactId ? { contactId } : {}
      }
    );
  }

  // Retrieve the contact associated with a session.
  getContactBySessionId(sessionId: string): Observable<Contact> {
    return this.getSessionById(sessionId).pipe(
      switchMap((session: Session) =>
        this.http.get<Contact>(
          `${this.contactsApiUrl}/${encodeURIComponent(session.contactId)}`
        )
      )
    );
  }

  // Retrieve the phone number associated with a session.
  getPhoneNumberBySessionId(sessionId: string): Observable<string> {
    return this.getContactBySessionId(sessionId).pipe(
      map((contact: Contact) => contact.phoneNumber)
    );
  }
}
