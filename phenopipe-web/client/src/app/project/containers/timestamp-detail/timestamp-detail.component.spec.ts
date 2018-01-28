import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TimestampDetailComponent } from './timestamp-detail.component';

describe('TimestampDetailComponent', () => {
  let component: TimestampDetailComponent;
  let fixture: ComponentFixture<TimestampDetailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TimestampDetailComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TimestampDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
