import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SampleGroupListComponent } from './sample-group-list.component';

describe('SampleGroupListComponent', () => {
  let component: SampleGroupListComponent;
  let fixture: ComponentFixture<SampleGroupListComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SampleGroupListComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SampleGroupListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
