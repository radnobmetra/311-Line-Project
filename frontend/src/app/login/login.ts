import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { Auth, signInWithEmailAndPassword } from '@angular/fire/auth';


@Component({
  imports: [FormsModule, CommonModule],
  selector: 'app-login',
  styleUrl: './login.css',
  templateUrl: './login.html',
})
export class Login {
  user = { email: '', password: '' };
  loginError: boolean = false;
  
  private router = inject(Router);
  private auth = inject(Auth);

  //true firebase validation
  login(): void {
    signInWithEmailAndPassword(this.auth, this.user.email, this.user.password)
      .then(() => {
        this.loginError = false;
        this.router.navigate(['/overview']);
      })
      .catch((error: any) => {
        console.error(error);
        this.loginError = true;
      });
  }
}