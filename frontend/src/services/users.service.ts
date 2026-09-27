import { Service, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { UserProfile } from '../interfaces/user-profile.interface';

@Service()
export class UserProfileService {
    http = inject(HttpClient);
    // Accounts API endpoint.
    apiUrl = 'http://localhost:3000/users';
   
    // Hardcoded a profile ID for testing. TODO: track active logged in user.
    currentProfileID: number = 1;

    // A fetch function that calls the endpoint to get the current user's profile data. 
    getCurrentProfile(): Observable<UserProfile> {
        const profileData =  this.http.get<UserProfile>(`${this.apiUrl}/${this.currentProfileID}`);
        return profileData;
    }
}
