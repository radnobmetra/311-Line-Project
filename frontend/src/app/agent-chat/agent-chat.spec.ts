import { ComponentFixture, TestBed } from '@angular/core/testing';
import { agentChat } from './agent-chat';

describe('agentChat', () => {
  let component: agentChat;
  let fixture: ComponentFixture<agentChat>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [agentChat],
    }).compileComponents();

    fixture = TestBed.createComponent(agentChat);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});