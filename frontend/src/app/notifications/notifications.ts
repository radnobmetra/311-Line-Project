import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { NotificationService } from '../../services/notifications.service';
import { notification } from '../../interfaces/notification.interface';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

@Component({
  imports: [],
  selector: 'notifications',
  styleUrl: './notifications.css',
  templateUrl: './notifications.html',
})

export class notifications implements OnInit {

    //path to default icon url
    default_icon_url = "envelope_icon.png";

    //path to icon url with red dot to indicate that there are unread notifications
    unread_icon_url = "envelope_icon_red_dot.png";

    //indicates if there are unread notifications
    unread_notifications = false;

    //path of notification icon
    icon_url: string;

    //controls if notification popup is hidden
    popup_hidden = true;
    
    notificationsService = inject(NotificationService);

    // Array that holds all notifications.
    notifications = signal<notification[]>([]);

    displayed_notifs = computed(() => {
        let tempArr = this.notifications();
        //sort notifications by date
        tempArr.sort(this.compare_dates_newest);
        //modify createdAt and read values to be easier to understand
        tempArr.forEach((element) => {
            if (element.read == "true") element.read = "read";
            else {
                element.read = "unread";
                //it's probably not good to update the icon here, but calling
                //updateIcon() in the constructor doesn't work because displayed_notifs
                //isn't computed when the constructor is run 
                if (this.icon_url == this.default_icon_url) 
                    this.icon_url = this.unread_icon_url;
            }
        });
        tempArr.forEach((element) => {
            let date = new Date(element.createdAt);
            element.createdAt = date.toUTCString();

        });
        return tempArr;
    });


    constructor() {
        this.notificationsService.getAllNotifications().pipe(takeUntilDestroyed()).subscribe({
        next: (notifications) => this.notifications.set(notifications),
        error: (err) => console.error("Messages polling error:", err)
    });
        this.icon_url = this.unread_icon_url;
        this.updateIcon();
    }

    //ngOnInit() runs when component is initialized. 

    ngOnInit(): void {

    }

    updateIcon() {
        //updates icon based on whether or not there are unread messages
        const unreadNotif = this.displayed_notifs().find((element) => element.read == "unread");
        if (unreadNotif) this.icon_url = this.unread_icon_url;
        else this.icon_url = this.default_icon_url;
    }

    toggleNotifications() {
        //toggle popup open or closed
        this.popup_hidden = !this.popup_hidden; 
    }

    compare_dates_newest(a: any, b: any) {
        //older dates are sorted after newer dates
        let a_int = Date.parse(a.createdAt);
        let b_int = Date.parse(b.createdAt);
        if (a_int < b_int) return 1;    //a is less recent -> sort a after b
        if (a_int > b_int) return -1;   //a is more recent -> sort a before b
        return 0;   //a == b -> return 0
    }

    deleteNotification(notif_id:any) {
        //This function runs when the user selects the delete button for a notification.

        //have the service connect to the db and delete the notification
        this.notificationsService.Delete(notif_id);
        //update the notifications icon
        this.updateIcon();
    }

    markAsRead(notif_id:any) {
        //This function runs when the user's cursor goes over a notification.

        //if notification is marked as unread, call notificationsService.markAsread()
        //to set it to read
        const notif = this.displayed_notifs().find((element) => element.id == notif_id);

        if (notif && (notif.read == "unread")) {
            this.notificationsService.markAsRead(notif_id);
            this.updateIcon();
        }
    }
}