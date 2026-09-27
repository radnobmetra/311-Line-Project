import { Service, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Contact } from '../interfaces/contact.interface';

@Service()
export class ContactsService {
    http = inject(HttpClient);
    // Contacts API endpoint.
    apiUrl = 'http://localhost:3000/contacts';

    // A fetch function that calls the endpoint to get all contacts. 
    getAllContacts(): Observable<Contact[]> {
        const contactsData =  this.http.get<Contact[]>(`${this.apiUrl}`);
        return contactsData;
    }

    // A fetch function that calls the endpoint to get a specific contact by ID. 
    getContactById(id: number): Observable<Contact> {
        const contactData =  this.http.get<Contact>(`${this.apiUrl}/${id}`);
        return contactData;
    }
}