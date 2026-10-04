import { Component, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Message } from '../../interfaces/message.interface';
import { MessagesService } from '../../services/messages.service';
import { ActivatedRoute } from '@angular/router';

@Component({
  imports: [DatePipe],
  selector: 'app-messages',
  styleUrl: './messages.css',
  templateUrl: './messages.html',
})
export class Messages {
  sessionID = inject(ActivatedRoute).snapshot.paramMap.get('id') ?? "";

  // Inject the messages service so we can consume the messages polling service.
  messagesService = inject(MessagesService);
  // Array that holds all messages.
  messages = signal<Message[]>([]);

  constructor() {
    // New messages will be fetched here.
    // Must register takeUntilDestroyed() to unsubscribe when the component is destroyed to avoid
    // background memory leaks.
    // this.messagesService.pollNewMessages().pipe(takeUntilDestroyed()).subscribe({
    //   next: (messages) => this.messages.set(messages),
    //   error: (err) => console.error("Messages polling error:", err)
    // });


    this.messagesService.getAllMessagesBySessionId(this.sessionID).subscribe({
      next: (messages) => this.messages.set(messages),
      error: (err) => console.error("Messages polling error:", err)
    });
  }
}
