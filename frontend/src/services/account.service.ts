import { Service, inject } from '@angular/core';
import { UserProfile } from '../interfaces/user-profile.interface';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Service()
export class AccountService {
    http = inject(HttpClient);
    // Hardcoded a profile ID for testing. TODO: track active logged in user.
    currentProfileID: number = 0;
    // Accounts API endpoint.
    apiUrl = 'http://localhost:3000/accounts';

    // A fetch function that calls the endpoint to get the current user's profile data. 
    getCurrentProfile(): Observable<UserProfile> {
        const profileData =  this.http.get<UserProfile>(`${this.apiUrl}/${this.currentProfileID}`);
        return profileData;
    }
}
