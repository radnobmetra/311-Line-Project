import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  imports: [RouterLink],
  selector: 'notifications',
  styleUrl: './notifications.css',
  templateUrl: './notifications.html',
})
export class notifications {

    //indicates if there are unread notifications
    unread_notifications = false;
    icon_url = "envelope_icon.png"
    
    toggleNotifications() {

    }
}