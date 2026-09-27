// Development/Testing phase: Since we don't have access to a database or a backend yet, I decided to simulate
// incoming message locally without a Twilio account or sending a real SMS. With 'json-server', you can test 
// the dashboard by posting fake messages to 'db.json', and Angular poll for updates every 2 seconds. 
// See below for implementation. 
// On the web app, messages will be displayed in its own page at http://{host}/messages.
// How to test? Open the messages page, send a POST request (via Postman), and the new message should appear within about 2 s.
// POST request format example: 
// url: http://localhost:3000/messages
// body: {
//     "from": "+1987654321",
//     "body": "There is a pothole on 123 Street.",
//     "receivedAt": "09/13/2026 08:15 AM"
// }
// The above parameters is what Twilio sends to the backend.  
// =================================================================================================================
// Production Phase: However, during production the below implementation will be modified accordingly.
// According to Twilio documentation "https://static1.twilio.com/docs/messaging/guides/webhook-request", when Twilio receives messages,
// it makes a synchronous HTTP request to the message URL configured in the Twilio console. 
// When we set up a database and backend, we'd need to implement 3 things:
// 1. Setup our backend API webhook in Twilio console as explained here: https://static1.twilio.com/docs/messaging/services
// 2. When Twilio sends HTTP POST to our backend webhook, the backend handles the messages and saves it in the database.
// 3. The backend pushes updates to the dashboard over an HTTP connection, which is commonly called Server-Sent Events (SSE). 

import { Service, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, timer, switchMap, EMPTY, catchError } from 'rxjs';
import { Message } from '../interfaces/message.interface';

@Service()
export class MessagesService {
    http = inject(HttpClient);
    // SMS Messages mock API endpoint.  
    apiUrl = "http://localhost:3000/messages";

    // This function will poll new messages from the endpoint every 4 seconds.
    // pollNewMessages(): Observable<Message[]> {
    //     // switchMap switchs to the HTTP GET request stream every time the timer ticks (every 4 seconds).
    //     return timer(0, 4000).pipe(switchMap(() => 
    //         this.http.get<Message[]>(this.apiUrl)
    //         .pipe(catchError(error => { return EMPTY;})) // Keep polling after a failed request
    //     ));
    // }

    // Fetch messages per conversation.
    getAllMessagesPerConversation(conversationID: number): Observable<Message[]> {
        const contactData =  this.http.get<Message[]>(`${this.apiUrl}?_where={"conversationId":{"eq":"${conversationID}"}}`);
        return contactData;
    }
}
