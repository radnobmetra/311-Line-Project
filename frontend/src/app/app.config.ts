import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { routes } from './app.routes';
import { provideFirebaseApp, initializeApp } from '@angular/fire/app';
import { provideAuth, getAuth } from '@angular/fire/auth';

//firebase app creds
const firebaseConfig = {
  apiKey: "AIzaSyAaYEYeJPehAIFKHY5qZmItHa62lZpkRlU",
  authDomain: "admin-96a00.firebaseapp.com",
  projectId: "admin-96a00",
  storageBucket: "admin-96a00.firebasestorage.app",
  messagingSenderId: "816234126132",
  appId: "1:816234126132:web:983a99f65657193c23e361"
};

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    //run firebase
    provideFirebaseApp(() => initializeApp(firebaseConfig)),
    provideAuth(() => getAuth())
  ]
};