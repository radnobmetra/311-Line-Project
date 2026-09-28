import { Service, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, timer, switchMap, EMPTY, catchError } from 'rxjs';
import { RequestHistory } from '../interfaces/request-history';

@Service()
export class RequestHistoryService {
    http = inject(HttpClient);
    // requests history mock API endpoint.  
    apiUrl = "http://localhost:3000/requestHistory";

    // This function will poll new requests from the endpoint every 5 seconds.
    // pollNewServiceRequests(): Observable<ServiceRequest[]> {
    //     // switchMap switchs to the HTTP GET request stream every time the timer ticks (every 5 seconds).
    //     return timer(0, 5000).pipe(switchMap(() => 
    //         this.http.get<ServiceRequest[]>(this.apiUrl)
    //         .pipe(catchError(error => { return EMPTY;})) // Keep polling after a failed request
    //     ));
    // }

    getAllServiceRequests(): Observable<RequestHistory[]> {
        const requestsData =  this.http.get<RequestHistory[]>(`${this.apiUrl}`);
        return requestsData;
    }
}