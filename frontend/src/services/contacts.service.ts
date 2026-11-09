import { Service, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, switchMap } from 'rxjs';
import { Contact } from '../interfaces/contact.interface';
import { environment } from '../environments/environment';

@Service()
export class ContactsService {
    http = inject(HttpClient);
    // Contacts API endpoint.
    apiUrl = `${environment.apiUrl}/contacts`;


    // A fetch function that calls the endpoint to get all contacts. 
    getAllContacts(): Observable<Contact[]> {
        const contactsData =  this.http.get<Contact[]>(`${this.apiUrl}`);
        return contactsData;
    }

    // A fetch function that calls the endpoint to get a specific contact by ID. 
    getContactById(contactId: string): Observable<Contact> {
        const contactData =  this.http.get<Contact>(`${this.apiUrl}/${contactId}`);
        return contactData;
    }

    getPhoneNumberByContactId(contactId: string): Observable<string> {
        return this.getContactById(contactId).pipe(switchMap((contact: Contact) => {
                const phoneNumber = contact.phoneNumber;
                return new Observable<string>((observer) => {
                    observer.next(phoneNumber);
                    observer.complete();
                });
            }
        ));
    }
}