import { Service, signal, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, timer, switchMap, EMPTY, catchError } from 'rxjs';
import { ChatMessage, ServerMessage } from '../interfaces/chat-message.interface';

@Service()
export class AgentChatService {
    http = inject(HttpClient);
    // requests history mock API endpoint.  
    apiUrl = "http://localhost:5000";
    session_id = "";

    /*
    getSessionId() {
        const sessionId = this.http.get(`${this.apiUrl} + "/getSessionId"`);
        this.session_id = sessionId;
    }

    getAllMessages(): Observable<ChatMessage[]> {
        const requestsData = this.http.get<ChatMessage[]>(`${this.apiUrl}`);
        return requestsData;
    }
    */

    sendMessage(message: string): Observable<ChatMessage> {
        let msgJson = JSON.stringify({ 'message': message });

        //send message and get server response (agent's response)

        const serverResponse = this.http.post<ChatMessage>(
            `${this.apiUrl}/sendMessage`, { 'message': message });

        return serverResponse;
    }
}