import { ActivatedRoute } from '@angular/router';
import { Component, inject, signal } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { PhonePipe } from '../../pipes/phone.pipe';
import { SessionsService } from '../../services/sessions.service';

@Component({
  imports: [RouterLink, RouterLinkActive, RouterOutlet, PhonePipe],
  selector: 'app-session-details',
  styleUrl: './session-details.css',
  templateUrl: './session-details.html',
})
export class SessionDetails {
  // Get the session ID from the route parameters. 
  sessionID = inject(ActivatedRoute).snapshot.paramMap.get('id') ?? "";

  // Inject the sessions service to fetch sessions.
  sessionsService = inject(SessionsService);
  phoneNumber = signal<string>("");
  
  constructor() {
    // If a session ID is provided, fetch the phone number for that session.
    if (this.sessionID) {
      // Retrieve phone number related to this session.
      this.sessionsService.getPhoneNumberBySessionId(this.sessionID).subscribe({
        next: (data) => this.phoneNumber.set(data),
        error: (err) => console.error("error:", err)
      });
    }
  }
}
