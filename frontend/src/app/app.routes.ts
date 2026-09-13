import { Routes } from '@angular/router';
import { Overview } from './overview/overview';
import { Settings } from './settings/settings';
import { Requests } from './requests/requests';
import { Analytics } from './analytics/analytics';

export const routes: Routes = [
    {path: 'overview', component: Overview},
    {path: 'settings', component: Settings},
    {path: 'analytics', component: Analytics},
    { path: 'requests', component: Requests},
    {path: '', redirectTo: '/overview', pathMatch: 'full'}
];
