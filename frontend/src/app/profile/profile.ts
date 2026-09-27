import { Component, inject, signal } from '@angular/core';
import { UserProfile } from '../../interfaces/user-profile.interface';
import { UserProfileService } from '../../services/users.service';

@Component({
  imports: [],
  selector: 'app-profile',
  styleUrl: './profile.css',
  templateUrl: './profile.html',
})
export class Profile {
  // Must inject the account service so it can be used for fetching the profile data. 
  userProfileService: UserProfileService = inject(UserProfileService);
  // Profile details will be stored here as a signal value.
  profileDetails = signal<UserProfile|null>(null);
  
  
  constructor() {
    // Fetch current profile data from account service.
    this.userProfileService.getCurrentProfile().subscribe({
      next: (profileData) => this.profileDetails.set(profileData),
      error: (err) => console.error("Error fetching data:", err)
    });
  }

  // TODO
  changePassword()
  {
    alert("Todo Later");
  }
}
