import { Component, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { PhonePipe } from '../../pipes/phone.pipe';
import { Contact } from '../../interfaces/contact.interface';
import { ContactsService } from '../../services/contacts.service';
import { tableToCsv } from '../utils/exportToCSV';

@Component({
    imports: [RouterLink, DatePipe, PhonePipe],
    selector: 'app-contacts',
    styleUrl: './contacts.css',
    templateUrl: './contacts.html',
})
export class Contacts {
    // Inject the contacts service to fetch contacts from the db.
    contactsService = inject(ContactsService);

    // Array to store all available contacts
    contacts = signal<Contact[]>([]);

    loading = signal<boolean>(true);
    errorMessage = signal<string>('');

    constructor() {
        this.loading.set(true);
        this.errorMessage.set('');

        // Retrieve all contacts from the db.
        this.contactsService.getAllContacts().subscribe({
            next: (contactsData) => { 
                this.contacts.set(contactsData); 

                this.loading.set(false);
            },
            error: (err) => {
                console.error("Error fetching data:", err);

                this.errorMessage.set('Unable to load contacts. Check that the Flask backend is running.');
                this.loading.set(false);
            }
        });
    }

    onExport(): void {
        let rows = this.contacts();
        // Calls the export utility.
        tableToCsv(rows, 'contacts');
    }
}
