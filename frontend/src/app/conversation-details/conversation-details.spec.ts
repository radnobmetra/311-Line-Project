import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ConversationDetails } from './conversation-details';

describe('ConversationDetails', () => {
  let component: ConversationDetails;
  let fixture: ComponentFixture<ConversationDetails>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ConversationDetails],
    }).compileComponents();

    fixture = TestBed.createComponent(ConversationDetails);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
