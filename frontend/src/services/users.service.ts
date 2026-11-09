import { Service, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { UserProfile } from '../interfaces/user-profile.interface';
import { environment } from '../environments/environment';

@Service()
export class UserProfileService {
    http = inject(HttpClient);
    // User API endpoint.
    apiUrl = `${environment.apiUrl}/user`;
   
    // A fetch function that calls the endpoint to get the current user's profile data. 
    getCurrentProfile(): Observable<UserProfile> {
        const profileData =  this.http.get<UserProfile>(`${this.apiUrl}`);
        return profileData;
    }
}
