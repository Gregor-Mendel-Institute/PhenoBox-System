import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AnalysisLogViewComponent } from './analysis-log-view.component';

describe('AnalysisLogViewComponent', () => {
  let component: AnalysisLogViewComponent;
  let fixture: ComponentFixture<AnalysisLogViewComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AnalysisLogViewComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AnalysisLogViewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
