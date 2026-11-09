import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap, provideRouter } from '@angular/router';
import { Observable, of } from 'rxjs';

import { Sessions } from './sessions';
import { Session } from '../../interfaces/session.interface';
import { SessionEvaluation, SessionsService } from '../../services/sessions.service';

// Sessions returned by the stubbed backend service.
const SESSIONS: Session[] = [
  {
    id: 'session-1001',
    contactId: '+15550001001',
    status: 'ACTIVE',
    startedAt: '2026-01-01T10:00:00Z',
    lastMessageAt: '2026-01-01T10:05:00Z',
  },
  {
    id: 'session-2002',
    contactId: '+15550002002',
    status: 'ACTIVE',
    startedAt: '2026-01-02T10:00:00Z',
    lastMessageAt: '2026-01-02T10:05:00Z',
  },
  {
    id: 'conv-abc-3003',
    contactId: '+15550003003',
    status: 'CLOSED',
    startedAt: '2026-01-03T10:00:00Z',
    lastMessageAt: '2026-01-03T10:05:00Z',
  },
];

// Stub the backend so the component can be created without HTTP calls.
class SessionsServiceStub {
  getAllSessions(): Observable<Session[]> {
    return of(SESSIONS);
  }

  getSessionsPerContact(): Observable<Session[]> {
    return of(SESSIONS);
  }

  getSessionEvaluations(): Observable<Record<string, SessionEvaluation | null>> {
    return of({});
  }
}

describe('Sessions', () => {
  let component: Sessions;
  let fixture: ComponentFixture<Sessions>;

  // Reads the session IDs currently rendered in the table, in display order.
  function renderedSessionIds(): string[] {
    const rows = Array.from(
      fixture.nativeElement.querySelectorAll('tbody tr')
    ) as HTMLTableRowElement[];

    return rows.map(row => row.cells[0].textContent?.trim() ?? '');
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
      imports: [Sessions],
      providers: [
        provideRouter([]),
        {
          provide: ActivatedRoute,
          useValue: { snapshot: { paramMap: convertToParamMap({}) } },
        },
        { provide: SessionsService, useValue: new SessionsServiceStub() },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(Sessions);
    component = fixture.componentInstance;
    fixture.detectChanges();
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render all sessions when the search bar is empty', () => {
    expect(renderedSessionIds().length).toBe(3);
    expect(renderedSessionIds()).toContain('session-1001');
    expect(renderedSessionIds()).toContain('session-2002');
    expect(renderedSessionIds()).toContain('conv-abc-3003');
  });

  it('should filter the table to the session ID typed in the search bar', () => {
    typeInSearchBar('2002');

    expect(renderedSessionIds()).toEqual(['session-2002']);
  });

  it('should match partial session IDs case-insensitively', () => {
    typeInSearchBar('abc');

    expect(renderedSessionIds()).toEqual(['conv-abc-3003']);
  });

  it('should ignore leading and trailing whitespace in the search input', () => {
    typeInSearchBar('  1001  ');

    expect(renderedSessionIds()).toEqual(['session-1001']);
  });

  it('should show the empty state when no session matches the search', () => {
    typeInSearchBar('does-not-exist');

    expect(renderedSessionIds()).toEqual([]);

    const emptyState = fixture.nativeElement.querySelector(
      '.empty-state'
    ) as HTMLElement | null;

    expect(emptyState?.textContent).toContain(
      'No sessions match the current search or outcome filter'
    );
  });

  it('should show every session again once the search is cleared', () => {
    typeInSearchBar('2002');
    expect(renderedSessionIds()).toEqual(['session-2002']);

    typeInSearchBar('');
    expect(renderedSessionIds().length).toBe(3);
  });

  it('should also filter when the search signal is set directly', () => {
    component.searchInput.set('1001');
    fixture.detectChanges();

    expect(renderedSessionIds()).toEqual(['session-1001']);
  });
});
