import { Routes } from '@angular/router';
import { Overview } from './overview/overview';
import { Settings } from './settings/settings';
import { Requests } from './requests/requests';
import { Analytics } from './analytics/analytics';
import { Login } from './login/login';
import { guardian } from './guardian'; 

export const routes: Routes = [
    // { path: 'login', component: Login }, //login page
    // { path: 'overview', component: Overview, canActivate: [guardian] }, //guadian ensures valid entry
    // { path: 'settings', component: Settings, canActivate: [guardian] },
    // { path: 'analytics', component: Analytics, canActivate: [guardian] },
    // { path: 'requests', component: Requests, canActivate: [guardian] },
    // { path: '', redirectTo: '/login', pathMatch: 'full' } //redirct

    { path: 'login', component: Login }, //login page
    { path: 'overview', component: Overview,  }, //guadian ensures valid entry
    { path: 'settings', component: Settings,  },
    { path: 'analytics', component: Analytics,  },
    { path: 'requests', component: Requests,  },
    { path: '', redirectTo: '/overview', pathMatch: 'full' } //redirct
];