import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AnalysisDashboardComponent } from './analysis-dashboard.component';

describe('AnalysisDashboardComponent', () => {
  let component: AnalysisDashboardComponent;
  let fixture: ComponentFixture<AnalysisDashboardComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AnalysisDashboardComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AnalysisDashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
