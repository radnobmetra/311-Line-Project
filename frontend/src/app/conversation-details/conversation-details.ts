import { ActivatedRoute } from '@angular/router';
import { Component, inject, signal } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  selector: 'app-conversation-details',
  styleUrl: './conversation-details.css',
  templateUrl: './conversation-details.html',
})
export class ConversationDetails {
  // Get the conversation ID from the route parameters. 
  conversationID = inject(ActivatedRoute).snapshot.paramMap.get('id') ?? "";

  
}
