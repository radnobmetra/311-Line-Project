import { Service, signal, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, timer, switchMap, EMPTY, catchError } from 'rxjs';
import { ChatMessage, ServerMessage } from '../interfaces/chat-message.interface';
import { environment } from '../environments/environment';

@Service()
export class AgentChatService {
    http = inject(HttpClient);
    // flask app API endpoint.  
    sendMsgApiUrl = `${environment.apiUrl}/sendMessage`;
    sendImgApiUrl = `${environment.apiUrl}/sendImage`;

    //user's id/username, used to get user's sessions
    user_number = "remote-chat-test"

    sendMessage(message: string): Observable<ChatMessage> {
        let msgJson = JSON.stringify({ 'message': message });

        //send message and get server response (agent's response or error message)
        const serverResponse = this.http.post<ChatMessage>(
            `${this.sendMsgApiUrl}`, { 'userNumber': this.user_number, 'message': message });

        return serverResponse;
    }

    sendImage(imageFile: File): Observable<ChatMessage> {
        //create a form to send the image in
        const formData = new FormData();
        //attach user id to form
        formData.append("userNumber", this.user_number);
        //attach file to form
        formData.append("userUpload", imageFile);

        const serverResponse = this.http.post<ChatMessage>(
            `${this.sendImgApiUrl}`, formData
        );
        console.log("image sent");
        return serverResponse;
    }
}