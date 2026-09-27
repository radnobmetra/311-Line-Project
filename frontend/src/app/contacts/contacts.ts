import { Component, inject, signal } from '@angular/core';
import { Contact } from '../../interfaces/contact.interface';
import { ContactsService } from '../../services/contacts.service';

@Component({
  imports: [],
  selector: 'app-contacts',
  styleUrl: './contacts.css',
  templateUrl: './contacts.html',
})
export class Contacts {
  contactsService = inject(ContactsService);

  contacts = signal<Contact[]>([]);

  constructor() {
    this.contactsService.getAllContacts().subscribe({
      next: (contactsData) => {this.contacts.set(contactsData);},
      error: (err) => console.error("Error fetching data:", err)
    });
  }
}
