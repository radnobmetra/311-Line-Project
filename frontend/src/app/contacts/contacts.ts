import { Component, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { PhonePipe } from '../../pipes/phone.pipe';
import { Contact } from '../../interfaces/contact.interface';
import { ContactsService } from '../../services/contacts.service';

@Component({
  imports: [DatePipe, RouterLink, PhonePipe],
  selector: 'app-contacts',
  styleUrl: './contacts.css',
  templateUrl: './contacts.html',
})
export class Contacts {
  // Inject the contacts service to fetch contacts from the db.
  contactsService = inject(ContactsService);

  // Array to store all available contacts
  contacts = signal<Contact[]>([]);

  constructor() {
    // Retrieve all contacts from the db.
    this.contactsService.getAllContacts().subscribe({
      next: (contactsData) => {this.contacts.set(contactsData);},
      error: (err) => console.error("Error fetching data:", err)
    });
  }
}
