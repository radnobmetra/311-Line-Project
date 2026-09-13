import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { Auth, authState } from '@angular/fire/auth';
import { map } from 'rxjs';

//checks if user has valid entru
export const guardian: CanActivateFn = (route,state) => {const auth = inject(Auth);
  const router = inject(Router);
  //checks tokens to keep or kick
  return authState(auth).pipe(
    map(user => {
      if (user) {
        return true; 
      } else {
        router.navigate(['/login']); 
        return false;
      }}) );
};