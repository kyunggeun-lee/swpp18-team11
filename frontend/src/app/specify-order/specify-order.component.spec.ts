import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SpecifyOrderComponent } from './specify-order.component';
import {SelectOptionComponent} from '../select-option/select-option.component';
import {HttpClientTestingModule} from '@angular/common/http/testing';
import {RouterTestingModule} from '@angular/router/testing';
import {Routes} from '@angular/router';
import {SelectFoodComponent} from '../select-food/select-food.component';
import {MyCartComponent} from '../my-cart/my-cart.component';
import {PaymentComponent} from '../payment/payment.component';
import {HttpClient} from '@angular/common/http';
import {of} from 'rxjs';
import {Purchasable} from '../purchasable';
import {Option} from '../option';

fdescribe('SpecifyOrderComponent', () => {
  let component: SpecifyOrderComponent;
  let fixture: ComponentFixture<SpecifyOrderComponent>;
  let http: HttpClient;
  const purchasableStub: Partial<Purchasable> = {
    id: 1,
    name: 'p',
    thumbnail: 'x',
    base_price: 1000
  };
  const routes: Routes = [
    { path: '', redirectTo: '/order', pathMatch: 'full'},
    { path: 'order', component: SelectFoodComponent },
    { path: 'order/:menu_id', component: SpecifyOrderComponent },
    { path: 'mycart', component: MyCartComponent },
    { path: 'payment', component: PaymentComponent },
  ];

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [
        SpecifyOrderComponent,
        SelectOptionComponent,
        SelectFoodComponent,
        MyCartComponent,
        PaymentComponent
      ],
      imports: [
        HttpClientTestingModule,
        RouterTestingModule.withRoutes(routes)
      ]
    })
    .compileComponents();
    http = TestBed.get(HttpClient);
    spyOn(http, 'get').and.callFake(() =>
      of({success: true, data: purchasableStub as Purchasable})
    );
  }));

  beforeEach((done) => {
    fixture = TestBed.createComponent(SpecifyOrderComponent);
    component = fixture.componentInstance;
    done();
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
    expect(component.product).toBeDefined();
    expect(component.product.base_price).toBe(1000);
  });

  it('should expand options', () => {
    expect(component.expandOption).toBe(false);
    component.openOptionSelectPage();
    expect(component.expandOption).toBe(true);
  });

  it('should increment/decrement quantity', () => {
    expect(component.product.quantity).toBe(1);
    expect(component.product.total_price).toBe(1000);
    component.decrement();
    expect(component.product.quantity).toBe(1);
    expect(component.product.total_price).toBe(1000);
    component.increment();
    expect(component.product.quantity).toBe(2);
    expect(component.product.total_price).toBe(2000);
    for (let i = 0; i < 100; i++) {
      component.increment();
    }
    expect(component.product.quantity).toBe(100);
    expect(component.product.total_price).toBe(1000 * 100);
  });

  it('should update options', () => {
    const options: Option[] = [{
      id: 1,
      name: 'o',
      base_price: 100,
      max_capacity: 100,
      quantity: 1,
      total_price: 100
    }];

    component.updateOptionChange(options);
    expect(component.product.total_price).toBe(1100);
  });
});
