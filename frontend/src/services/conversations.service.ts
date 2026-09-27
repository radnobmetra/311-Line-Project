import { Service, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Conversation } from '../interfaces/conversation.interface';

@Service()
export class ConversationsService {
    http = inject(HttpClient);
    // conversations API endpoint.
    apiUrl = 'http://localhost:3000/conversations';

    // A fetch function that calls the endpoint to get all conversations. 
    getAllConversations(): Observable<Conversation[]> {
        const conversationsData =  this.http.get<Conversation[]>(`${this.apiUrl}`);
        return conversationsData;
    }
}