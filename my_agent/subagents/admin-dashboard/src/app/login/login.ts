import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms'; // Allows ngModel to be used for two-way data binding.
import { CommonModule } from '@angular/common'; // Provides common directives like ngIf for conditional rendering.
import{ Router } from '@angular/router';

@Component({
  imports: [FormsModule, CommonModule],
  selector: 'app-login',
  styleUrl: './login.css',
  templateUrl: './login.html',
})
export class Login {
  user={
    email: '',
    password: ''
  };
  storedUser={
    email: 'admin@cityofsacramento.org',
    password: 'Sac@2026'
  }
  
  loginError:boolean=false;

  router = inject(Router);

  // Boolean function that only returns true if the email and password inputs match the stored user credentials.
  validateLogin(email: string, password: string): boolean {
    return this.storedUser.email === email && this.storedUser.password === password;
  }

  login(): void {
    if (this.validateLogin(this.user.email, this.user.password)) {
      // Store the logged-in user's email in local storage.
      localStorage.setItem('loggedInUser', JSON.stringify(this.user.email));
      // Will keep the error message hidden.
      this.loginError = false;
      // Redirect to the dashboard if login is successful.
      this.router.navigate(['/dashboard']);
    } else {
      // Will display the error message if the login fails.
      this.loginError = true;
    }
  }
}
