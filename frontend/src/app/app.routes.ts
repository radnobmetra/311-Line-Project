import { Routes } from '@angular/router';
import { Overview } from './overview/overview';
import { Settings } from './settings/settings';
import { Requests } from './requests/requests';
import { Analytics } from './analytics/analytics';
import { Login } from './login/login';
import { guardian } from './guardian';
import { Profile } from './profile/profile';
import { Messages } from './messages/messages';
import { Contacts } from './contacts/contacts';
import { Sessions } from './sessions/sessions';
import { SessionDetails } from './session-details/session-details';
import { ServiceRequests } from './service-requests/service-requests';
import { RequestDetails } from './request-details/request-details';

export const routes: Routes = [
    // Disabled authentication temporarily until we are done creating all pages.

     { path: 'login', component: Login }, //login page
     { path: 'overview', component: Overview, canActivate: [guardian] }, //guadian ensures valid entry
     { path: 'settings', component: Settings, canActivate: [guardian] },
     { path: 'analytics', component: Analytics, canActivate: [guardian] },
     { path: 'requests', component: Requests, canActivate: [guardian] },
     { path: 'messages', component: Messages, canActivate: [guardian] },
     { path: 'events', component: Events, canActivate: [guardian] },
     { path: 'profile', component: Profile, canActivate: [guardian] },
     { path: 'contacts', component: Contacts, canActivate: [guardian] },
     { path: 'sessions', component: Sessions, canActivate: [guardian] },
     { path: 'sessions/:id', component: Sessions, canActivate: [guardian] },
     { path: 'session-details/:id', component: SessionDetails, 
        children: [
            { path: 'messages', component: Messages },
            { path: 'service-requests', component: ServiceRequests },
            { path: '', redirectTo: 'messages', pathMatch: 'full'}
        ], 
        canActivate: [guardian] },
    { path: 'service-requests', component: ServiceRequests, canActivate: [guardian] },
    { path: 'request-details/:id', component: RequestDetails, canActivate: [guardian] },
    { path: '', redirectTo: '/login', pathMatch: 'full' } //redirct
/*
    { path: 'login', component: Login }, //login page
    { path: 'overview', component: Overview,  }, //guadian ensures valid entry
    { path: 'settings', component: Settings,  },
    { path: 'analytics', component: Analytics,  },
    { path: 'requests', component: Requests,  },
    { path: 'messages', component: Messages,  },
    { path: 'profile', component: Profile,  },
    { path: 'events', component: Events,  },
    { path: '', redirectTo: '/overview', pathMatch: 'full' } //redirct */
];
