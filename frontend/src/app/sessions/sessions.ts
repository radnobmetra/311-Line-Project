import { FormsModule } from '@angular/forms'; // Permits the use of ngModel in the .html
import { form, FormField } from '@angular/forms/signals';

import { ActivatedRoute } from '@angular/router';
import { Component, inject, signal, computed  } from '@angular/core';
import { DatePipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { PhonePipe } from '../../pipes/phone.pipe';
import { SessionDetails } from '../../interfaces/session-details.interface';
import { SessionsService } from '../../services/sessions.service';
import { ContactsService } from '../../services/contacts.service';

interface sortFilterInput {
    sortDate: string;
    filterStartDate: string;
    filterEndDate: string;
    filterTopic: string;
}

@Component({
  imports: [DatePipe, RouterLink, PhonePipe, FormsModule],
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

  // Signal array to hold the raw request records.
  requests = signal<SessionDetails[]>([]);

  // Will hold the search bar input.
  searchInput = signal<string>('');

  // Store session + related phone number.
  sessionMap = signal<Map<string, SessionDetails>>(new Map());

  // Track the current outcome filter state
  currentFilter = signal<string>('ALL');

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
    sortFilterModel = signal<sortFilterInput>({
        sortDate: "",
        filterStartDate: "",
        filterEndDate: "",
        filterTopic: "",
    });
    sortFilterForm = form(this.sortFilterModel);
      // This function applies searching and filtering to the requests.
    displayed_reqs = computed(() => {
        // The "..." unpacks the signal array into a normal array so that it can be filtered and sorted.
        let processed_records = [...this.requests()];

        // If any of the fields are null, set them to an empty string so that
        // the search bar and filter functions don't throw errors.
        processed_records.forEach((record) => {
            if (record.session.id == null) record.session.id = "";
            if (record.phoneNumber == null) record.phoneNumber = "";
        });

        // Search Bar functionality
        const query = this.searchInput().toLowerCase().trim();
        if (query !== '') {
            processed_records = processed_records.filter(record => {
                if (
                record.session.id.toString().includes(query) ||
                record.phoneNumber.toLowerCase().includes(query) //||
                // record.topic.toLowerCase().includes(query) ||
                // record.createdAt.toLowerCase().includes(query)
                ) {
                    return true;
                }
                else {
                    // this.toggleSelectedMsg(record.id, true);
                    return false;
                }
            });
        }

        // Filter by id
        const idFilter = this.sortFilterForm.filterTopic().value();
        if (idFilter) {
            processed_records = processed_records.filter(
                (record) => record.session.id == idFilter);
        }

        return processed_records;
    });

  // Update the active filter when the dropdown changes
  setFilter(event: Event) {
    const selectElement = event.target as HTMLSelectElement;
    this.currentFilter.set(selectElement.value);
  }

  // Helper method to safely extract the final_outcome from the system event
  getFinalOutcome(session: any): string | null {
    if (!session || !session.events) return null;

    const outcomeEvent = session.events.find((e: any) =>
      e.author === 'system' &&
      e.content?.parts?.[0]?.text?.includes('final_outcome')
    );

    if (outcomeEvent) {
      try {
        const data = JSON.parse(outcomeEvent.content.parts[0].text);
        return data.final_outcome;
      } catch {
        return null;
      }
    }
    return null;
  }

  // Returns the sessions filtered by outcome, then sorted by ID
  get sortedSessions(): SessionDetails[] {
    const filter = this.currentFilter();
    const allSessions = Array.from(this.sessionMap().values());
    console.log("First session payload:", allSessions[0]?.session);

    const filteredSessions = allSessions.filter(item => {
      if (filter === 'ALL') return true;
      const outcome = this.getFinalOutcome(item.session);
      return outcome?.toUpperCase() === filter.toUpperCase();
    });

    return filteredSessions.sort(
      (a, b) => Number(a.session.id) - Number(b.session.id)
    );
  }

}
