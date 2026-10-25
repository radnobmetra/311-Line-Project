import { inject } from '@angular/core';
import { HttpInterceptorFn } from '@angular/common/http';
import { Auth } from '@angular/fire/auth';
import { from, switchMap } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  // Only attach credentials to our own relative API URLs.
  if (!req.url.startsWith('/api/')) {
    return next(req);
  }

  const auth = inject(Auth);

  // Wait until Firebase finishes restoring the login session.
  return from(auth.authStateReady()).pipe(switchMap(() => {
      const user = auth.currentUser;

      if (!user) {
        // The backend will reject protected requests with 401.
        return next(req);
      }

      // Retrieves the current token and refreshes it when necessary
      return from(user.getIdToken()).pipe(switchMap(token => {
          const authenticatedRequest = req.clone({
            setHeaders: {
              Authorization: `Bearer ${token}`
            }
          });

          return next(authenticatedRequest);
        })
      );
    })
  );
};