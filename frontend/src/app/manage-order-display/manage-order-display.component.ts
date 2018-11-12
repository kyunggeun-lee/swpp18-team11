import { Component, OnInit, OnDestroy } from '@angular/core';
import { ManageOrderStateService } from '../manage-order-state.service';
import { Ticket } from '../ticket';
import { TicketChange } from '../ticket-change';

import { Observable, Subscription } from 'rxjs';
import { map, take } from 'rxjs/operators';

import { TtsService } from '../tts.service';

@Component({
  selector: 'app-manage-order-display',
  templateUrl: './manage-order-display.component.html',
  styleUrls: ['./manage-order-display.component.css']
})
export class ManageOrderDisplayComponent implements OnInit, OnDestroy  {
  public doneTickets$: Observable<Ticket[]>;
  public todoDoingTickets$: Observable<Ticket[]>;
  public ticketChanges$: Observable<TicketChange>;

  public doneSubscription: Subscription;

  constructor(private manageOrderStateService: ManageOrderStateService, private ttsService: TtsService) { }

  ngOnInit() {
    const tickets$ = this.manageOrderStateService.tickets$;
    this.todoDoingTickets$ = tickets$.pipe(map(tickets => tickets.filter(x => x.state !== 'done')));
    this.doneTickets$ = tickets$.pipe(map(tickets => tickets.filter(x => x.state === 'done')));
    this.ticketChanges$ = this.manageOrderStateService.ticketChanges$;

    this.ticketChanges$.subscribe(ticketChange => {
      const ticket = ticketChange.ticket;
      if (ticket.state === 'done') {
        this.ttsService.playTTS(ticket);
      }
    });
  }

  ngOnDestroy() {
    if (this.doneSubscription) {
      this.doneSubscription.unsubscribe();
    }
  }
}
