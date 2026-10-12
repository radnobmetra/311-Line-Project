import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FlaggedConvo } from './flagged-convo';

describe('FlaggedConvo', () => {
  let component: FlaggedConvo;
  let fixture: ComponentFixture<FlaggedConvo>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FlaggedConvo],
    }).compileComponents();

    fixture = TestBed.createComponent(FlaggedConvo);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
