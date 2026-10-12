import { Service, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, timer, switchMap, EMPTY, catchError } from 'rxjs';
import { notification } from '../interfaces/notification.interface';

@Service()
export class NotificationService {
    http = inject(HttpClient);
    // notifications mock API endpoint.  
    apiUrl = "http://localhost:3000/notifications";

    getAllNotifications(): Observable<notification[]> {
        const notificationsData =  this.http.get<notification[]>(`${this.apiUrl}`);
        return notificationsData;
    }

    markAsRead(id: any) {
        // to do: connect to db and set notification as read
        console.log("notification marked as read (id = " + id + ")");
    }

    Delete(id: any) {
        //to do: delete notification from db
        console.log("notification deleted (id = " + id + ")");
    }
}