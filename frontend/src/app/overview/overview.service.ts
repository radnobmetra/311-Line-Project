import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
    providedIn: 'root'
})

export class OverviewService {
    API_URL = 'http://localhost:3000/ticket_counts';

    constructor(private _httpclient:HttpClient) { 

    }

    showdata() {
        return this._httpclient.get(this.API_URL);
    }

}