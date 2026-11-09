import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap, provideRouter } from '@angular/router';
import { Observable, of } from 'rxjs';

import { ServiceRequests } from './service-requests';
import { ServiceRequest } from '../../interfaces/service-request.interface';
import { ServiceRequestsService } from '../../services/service-requests.service';

// Service requests returned by the stubbed backend service.
const SERVICE_REQUESTS = [
  {
    id: '1001',
    sessionId: 'session-1',
    categoryId: 'cat-1',
    title: 'Pothole on Main St',
    description: 'Deep pothole in the northbound lane.',
    status: 'OPEN',
    priority: 'HIGH',
    address: '123 Main St',
    latitude: 0,
    longitude: 0,
    createdAt: '2026-01-01T10:00:00Z',
    updatedAt: '2026-01-01T10:00:00Z',
    resolvedAt: '',
    closedAt: '',
  },
  {
    id: '1002',
    sessionId: 'session-2',
    categoryId: 'cat-2',
    title: 'Broken streetlight',
    description: 'Streetlight has been out for a week.',
    status: 'CLOSED',
    priority: 'LOW',
    address: '456 Oak Ave',
    latitude: 0,
    longitude: 0,
    createdAt: '2026-01-02T11:00:00Z',
    updatedAt: '2026-01-02T11:00:00Z',
    resolvedAt: '2026-01-03T09:00:00Z',
    closedAt: '2026-01-03T09:00:00Z',
  },
  {
    id: '1003',
    sessionId: 'session-3',
    categoryId: 'cat-3',
    title: 'Graffiti removal',
    description: 'Graffiti on the bus shelter.',
    status: 'PENDING',
    priority: 'MEDIUM',
    address: '789 Pine Rd',
    latitude: 0,
    longitude: 0,
    createdAt: '2026-01-03T12:00:00Z',
    updatedAt: '2026-01-03T12:00:00Z',
    resolvedAt: '',
    closedAt: '',
  },
] as ServiceRequest[];

// Stub the backend so the component can be created without HTTP calls.
class ServiceRequestsServiceStub {
  getAllServiceRequests(): Observable<ServiceRequest[]> {
    return of(SERVICE_REQUESTS);
  }

  getAllServiceRequestsBySessionId(): Observable<ServiceRequest[]> {
    return of(SERVICE_REQUESTS);
  }
}

describe('ServiceRequests', () => {
  let component: ServiceRequests;
  let fixture: ComponentFixture<ServiceRequests>;

  // Reads the service request IDs currently rendered in the table, in order.
  function renderedRequestIds(): string[] {
    const rows = Array.from(
      fixture.nativeElement.querySelectorAll('table tr')
    ) as HTMLTableRowElement[];

    // The first row holds the table headers, so skip it.
    return rows
      .filter(row => row.querySelector('td') !== null)
      .map(row => row.cells[0].textContent?.trim() ?? '');
  }

  // Types into the rendered search bar, exercising the ngModel binding.
  function typeInSearchBar(value: string): void {
    const input = fixture.nativeElement.querySelector(
      '#search'
    ) as HTMLInputElement;

    input.value = value;
    input.dispatchEvent(new Event('input'));
    fixture.detectChanges();
  }

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ServiceRequests],
      providers: [
        provideRouter([]),
        {
          provide: ActivatedRoute,
          useValue: { snapshot: { paramMap: convertToParamMap({}) } },
        },
        {
          provide: ServiceRequestsService,
          useValue: new ServiceRequestsServiceStub(),
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ServiceRequests);
    component = fixture.componentInstance;
    fixture.detectChanges();
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render every service request when the search bar is empty', () => {
    expect(renderedRequestIds()).toEqual(['1001', '1002', '1003']);
  });

  it('should filter the table by the service request ID typed in the search bar', () => {
    typeInSearchBar('1002');

    expect(renderedRequestIds()).toEqual(['1002']);
  });

  it('should match a partial service request ID', () => {
    typeInSearchBar('100');

    expect(renderedRequestIds()).toEqual(['1001', '1002', '1003']);
  });

  it('should match the title case-insensitively', () => {
    typeInSearchBar('STREETLIGHT');

    expect(renderedRequestIds()).toEqual(['1002']);
  });

  it('should match the status case-insensitively', () => {
    typeInSearchBar('pending');

    expect(renderedRequestIds()).toEqual(['1003']);
  });

  it('should ignore leading and trailing whitespace in the search input', () => {
    typeInSearchBar('  graffiti  ');

    expect(renderedRequestIds()).toEqual(['1003']);
  });

  it('should show the no-match state when nothing matches the search', () => {
    typeInSearchBar('nothing matches this');

    expect(renderedRequestIds()).toEqual([]);

    const emptyState = fixture.nativeElement.querySelector(
      '.empty-state'
    ) as HTMLElement | null;

    expect(emptyState?.textContent).toContain(
      'No service requests match the current search'
    );
  });

  it('should show every service request again once the search is cleared', () => {
    typeInSearchBar('1002');
    expect(renderedRequestIds()).toEqual(['1002']);

    typeInSearchBar('');
    expect(renderedRequestIds()).toEqual(['1001', '1002', '1003']);
  });

  it('should also filter when the search signal is set directly', () => {
    component.searchInput.set('1001');
    fixture.detectChanges();

    expect(renderedRequestIds()).toEqual(['1001']);
  });

  it('should not mutate the records loaded from the backend when searching', () => {
    typeInSearchBar('1002');

    expect(SERVICE_REQUESTS[0].title).toBe('Pothole on Main St');
    expect(SERVICE_REQUESTS[0].status).toBe('OPEN');
  });
});
