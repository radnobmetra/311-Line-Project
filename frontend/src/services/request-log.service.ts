import { Service, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, timer, switchMap, EMPTY, catchError } from 'rxjs';
import { RequestLog } from '../interfaces/request-log';

@Service()
export class RequestLogService {
    http = inject(HttpClient);
    // requests history mock API endpoint.  
    apiUrl = "http://localhost:3000/requestLog";

    getAllServiceRequests(): Observable<RequestLog[]> {
        const requestsData =  this.http.get<RequestLog[]>(`${this.apiUrl}`);
        return requestsData;
    }
}