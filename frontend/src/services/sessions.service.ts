import { Service, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, switchMap } from 'rxjs';
import { Session } from '../interfaces/session.interface';
import { Contact } from '../interfaces/contact.interface';

@Service()
export class SessionsService {
    http = inject(HttpClient);
    // sessions API endpoint.
    apiUrl = 'http://localhost:3000/sessions';
    // contacts API endpoint.
    contactsApiUrl = 'http://localhost:3000/contacts';

    // A fetch function that calls the endpoint to get all sessions.
    getAllSessions(): Observable<Session[]> {
        const sessionsData =  this.http.get<Session[]>(`${this.apiUrl}`);
        return sessionsData;
    }

    // A fetch function that calls the endpoint to get a specific session by ID.
    getSessionById(sessionId: string): Observable<Session> {
        const sessionData =  this.http.get<Session>(`${this.apiUrl}/${sessionId}`);
        return sessionData;
    }

    // A fetch function that calls the endpoint to get all sessions for a specific contact by contact ID.
    getSessionsPerContact(contactId: string): Observable<Session[]> {
        const sessionsData =  this.http.get<Session[]>(`${this.apiUrl}?_where={"contactId":{"eq":"${contactId}"}}`);
        return sessionsData;
    }

    // A fetch function that calls the endpoint to get the contact associated with a specific session by session ID.
    getContactBySessionId(sessionId: string): Observable<Contact> {
        return this.getSessionById(sessionId).pipe(switchMap((session: Session) => {
                const contactId = session.contactId;
                return this.http.get<Contact>(`${this.contactsApiUrl}/${contactId}`);
            })
        );
    }

    // A fetch function that calls the endpoint to get the phone number associated with a specific session by session ID.
    getPhoneNumberBySessionId(sessionId: string): Observable<string> {
        return this.getContactBySessionId(sessionId).pipe(switchMap((contact: Contact) => {
                const phoneNumber = contact.phoneNumber;
                return new Observable<string>((observer) => {
                    observer.next(phoneNumber);
                    observer.complete();
                });
            })
        );
    }
}