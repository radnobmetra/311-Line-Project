import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ServiceRequests } from './service-requests';

describe('ServiceRequests', () => {
  let component: ServiceRequests;
  let fixture: ComponentFixture<ServiceRequests>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ServiceRequests],
    }).compileComponents();

    fixture = TestBed.createComponent(ServiceRequests);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
