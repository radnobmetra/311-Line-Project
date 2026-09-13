import { Routes } from '@angular/router';
import { Home } from './components/home/home';
import { TempPage } from './components/temp-page/temp-page';

export const routes: Routes = [
    {
        path: '',
        title: 'Home',
        component: Home
    },
    {
        path: 'temp',
        title: 'Temporary Page',
        component: TempPage
    }
];

/*login page goes here, dashboard page goes here, 404 page goes here. NEED TO IMPLEMENT*/