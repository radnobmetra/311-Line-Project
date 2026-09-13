import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TempPage } from './temp-page';

describe('TempPage', () => {
  let component: TempPage;
  let fixture: ComponentFixture<TempPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TempPage],
    }).compileComponents();

    fixture = TestBed.createComponent(TempPage);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
