import { ActivatedRoute } from '@angular/router';
import { Component, inject, signal  } from '@angular/core';
import { DatePipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { PhonePipe } from '../../pipes/phone.pipe';
import { SessionDetails } from '../../interfaces/session-details.interface';
import { SessionsService } from '../../services/sessions.service';
import { ContactsService } from '../../services/contacts.service';

@Component({
  imports: [DatePipe, RouterLink, PhonePipe],
  selector: 'app-sessions',
  styleUrl: './sessions.css',
  templateUrl: './sessions.html',
})
export class Sessions {
  // Get the contact ID from the route parameters.
  contactID = inject(ActivatedRoute).snapshot.paramMap.get('id') ?? "";

  // Inject services.
  contactsService = inject(ContactsService);
  sessionsService = inject(SessionsService);

  // Store session + related phone number.
  sessionMap = signal<Map<string, SessionDetails>>(new Map());

  constructor() {
    // If a contact ID was provided.
    if (this.contactID) {
      // Get the phone number first.
      this.contactsService.getPhoneNumberByContactId(this.contactID).subscribe({
          next: (phoneNumber) => {
            // Then get the sessions belonging to the contact.
            this.sessionsService.getSessionsPerContact(this.contactID).subscribe({
                next: (sessionsData) => {
                  const map = new Map<string, SessionDetails>();

                  // For each session, add it to the map along with the phone number.
                  for (const session of sessionsData) {
                    map.set(session.id, {
                      session: session,
                      phoneNumber: phoneNumber
                    });
                  }
                  // Update the signal with the new map.
                  this.sessionMap.set(map);
                },
                error: (err) =>console.error("Error retrieving sessions:", err)});
          },
          error: (err) => console.error("Error retrieving phone number:", err)
        });
    } else {
      // Retrieve all sessions.
      this.sessionsService.getAllSessions().subscribe({
        next: (sessionsData) => {
          // For each session, retrieve the phone number related to that session.
          for (const session of sessionsData) {
            // Retrieve the phone number related to the session.
            this.sessionsService.getPhoneNumberBySessionId(session.id).subscribe({
                next: (phoneNumber) => {
                  // Update the sessionMap signal with the new session and phone number.
                  this.sessionMap.update((currentMap) => {
                    // Create a new Map so the signal detects the change.
                    const updatedMap = new Map(currentMap);

                    // Add the session and phone number to the map.
                    updatedMap.set(session.id, {
                      session: session,
                      phoneNumber: phoneNumber
                    });

                    // Return the updated map to update the signal.
                    return updatedMap;
                  });
                },
                error: (err) => console.error("Error retrieving phone number:", err)});
          }
        },
        error: (err) => console.error("Error retrieving sessions:", err)});
    }
  }

  // returns the sessions sorted by their ID.
  get sortedSessions(): SessionDetails[] {
    return Array.from(this.sessionMap().values()).sort(
      (a, b) => Number(a.session.id) - Number(b.session.id)
    );
  }
}