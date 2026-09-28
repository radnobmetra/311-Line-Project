import { ActivatedRoute } from '@angular/router';
import { Component, inject, signal  } from '@angular/core';
import { DatePipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { PhonePipe } from '../../pipes/phone.pipe';
import { Conversation } from '../../interfaces/conversation.interface';
import { ConversationsService } from '../../services/conversations.service';
import { ContactsService } from '../../services/contacts.service';

@Component({
  imports: [DatePipe, RouterLink, PhonePipe],
  selector: 'app-conversations',
  styleUrl: './conversations.css',
  templateUrl: './conversations.html',
})
export class Conversations {
  // Get the contact ID from the route parameters. 
  contactID = inject(ActivatedRoute).snapshot.paramMap.get('id') ?? "";
  
  // Inject the contacts service to fetch the phone number.
  contactsService = inject(ContactsService);
  // Inject the conversations service to fetch conversations.
  conversationsService = inject(ConversationsService);

  phoneNumber = signal<string>("");
  // Array to store conversations
  conversations = signal<Conversation[]>([]);
  
  
  constructor() {
    // Retrieve phone number related to this conversation.
    this.contactsService.getContactById(this.contactID).subscribe({
      next: (data) => this.phoneNumber.set(data.phoneNumber),
      error: (err) => console.error("error:", err)
    });

    // Retrieve conversations related to the current contact.
    this.conversationsService.getConversationsPerContact(this.contactID).subscribe({
      next: (conversationsData) => this.conversations.set(conversationsData),
      error: (err) => console.error("error:", err)
    });
  }

}
