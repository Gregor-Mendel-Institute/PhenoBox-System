import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TimestampAnalysisComponent } from './timestamp-analysis.component';

describe('TimestampAnalysisComponent', () => {
  let component: TimestampAnalysisComponent;
  let fixture: ComponentFixture<TimestampAnalysisComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TimestampAnalysisComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TimestampAnalysisComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
