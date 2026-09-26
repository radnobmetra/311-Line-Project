import { Component, OnInit } from '@angular/core';

@Component({
  imports: [],
  selector: 'notifications',
  styleUrl: './notifications.css',
  templateUrl: './notifications.html',
})

export class notifications implements OnInit{

    //path to default icon url
    default_icon_url = "white_envelope_icon.png";
    //path to icon url with red dot to indicate that there are unread notifications
    unread_icon_url = "white_envelope_icon_red_dot.png";
    //indicates if there are unread notifications
    unread_notifications = false;
    //path of notification icon
    icon_url = this.default_icon_url;
    //controls if notification popup is hidden
    popup_hidden = true;
    
    //use placeholder data for now since there's currently no backend 
    //for storing/creating/deleting notifications

    notifications = [
        {id: 1, seen: false, date: "2026/10/01", title: "Suspicious activity detected", content: "A conversation has been flagged for suspicious activity."},
        {id: 2, seen: false, date: "2026/09/05", title: "Welcome to the 311 text line dashboard!", content: "Visit the help page to learn more about this site."},
    ];

    displayed_notifs = this.notifications;

    //ngOnInit() runs when component is initialized. 

    ngOnInit(): void {
        //initialize notification icon
        if (this.unread_notifications == true) {
            this.icon_url = this.unread_icon_url;
        }
    }

    //toggles and updates notifications popup

    toggleNotifications() {
        
        //toggle popup open or closed
        this.popup_hidden = !this.popup_hidden; 

        //if notifications popup is open, display notifications
        if (!this.popup_hidden) {
            let displayed_notifs = this.notifications;
            displayed_notifs = displayed_notifs.sort(this.compare_dates_newest);
            this.displayed_notifs = displayed_notifs;
        }
    }

    compare_dates_newest(a: any, b: any) {
        //older dates are sorted after newer dates
        let a_int = Date.parse(a.date);
        let b_int = Date.parse(b.date);
        if (a_int < b_int) return 1;    //a is less recent -> sort a after b
        if (a_int > b_int) return -1;   //a is more recent -> sort a before b
        return 0;   //a == b -> return 0
    }

    deleteNotification(id_to_delete:any) {
        //This function runs when the user selects the delete button for the notification
        //with the id id_to_delete.
    }
}