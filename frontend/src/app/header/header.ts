import { Component, inject } from '@angular/core';
import { RouterLink, Router } from '@angular/router';
import { Auth, signOut } from '@angular/fire/auth'

@Component({
  imports: [RouterLink],
  selector: 'app-header',
  styleUrl: './header.css',
  templateUrl: './header.html',
})

export class Header {
  private auth = inject(Auth);  
  private router = inject(Router);

  logout() {
    console.log('logging out...');
    signOut(this.auth).then(() => {
      this.router.navigate(['/login']);
    });
  }
}