import { Component, signal } from '@angular/core';
import { Header } from './components/header/header';
import { NavBar } from './components/nav-bar/nav-bar';
import { RouterOutlet } from '@angular/router';

@Component({
  imports: [Header, NavBar, RouterOutlet],
  selector: 'app-root',
  styleUrl: './app.css',
  templateUrl: './app.html',
})
export class App {
  protected readonly title = signal('311-dashboard');
}
