import { Service, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Flagged } from '../interfaces/flagged-convo.interface';

@Service()
export class FlaggedService {
    http = inject(HttpClient);
    // Contacts API endpoint.
    apiUrl = 'http://localhost:3000/conversationFlags';

    // A fetch function that calls the endpoint to get all contacts. 
    getAllConvos(): Observable<Flagged[]> {
        const convoData =  this.http.get<Flagged[]>(`${this.apiUrl}`);
        return convoData;
    }

    // A fetch function that calls the endpoint to get a specific conversation by ID. 
    getConvoById(id: string): Observable<Flagged> {
        const convoData =  this.http.get<Flagged>(`${this.apiUrl}/${id}`);
        return convoData;
    }
}