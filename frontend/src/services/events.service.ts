import { Service, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, timer, switchMap, EMPTY, catchError } from 'rxjs';
import { EventMessage } from '../interfaces/events-db.interface';

@Service()
export class EventService {
    http = inject(HttpClient);
    apiUrl = "http://localhost:3000/events";

    // This function will poll new messages from the endpoint every 2 seconds.
    pollNewEvents(): Observable<EventMessage[]> {
        // switchMap switchs to the HTTP GET request stream every time the timer ticks (every 2 seconds).
        return timer(0, 2000).pipe(switchMap(() =>
            this.http.get<EventMessage[]>(this.apiUrl)
            .pipe(catchError(error => { return EMPTY;})) // Keep polling after a failed request
        ));
    }
}
