import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ChartWrapper } from './chart-wrapper';

describe('ChartWrapper', () => {
  let component: ChartWrapper;
  let fixture: ComponentFixture<ChartWrapper>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChartWrapper],
    }).compileComponents();

    fixture = TestBed.createComponent(ChartWrapper);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
