import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SampleGroupInputComponent } from './sample-group-input.component';

describe('SampleGroupInputComponent', () => {
  let component: SampleGroupInputComponent;
  let fixture: ComponentFixture<SampleGroupInputComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SampleGroupInputComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SampleGroupInputComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
