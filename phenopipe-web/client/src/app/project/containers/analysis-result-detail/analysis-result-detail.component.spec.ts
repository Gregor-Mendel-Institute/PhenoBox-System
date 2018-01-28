import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AnalysisResultDetailComponent } from './analysis-result-detail.component';

describe('AnalysisResultDetailComponent', () => {
  let component: AnalysisResultDetailComponent;
  let fixture: ComponentFixture<AnalysisResultDetailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AnalysisResultDetailComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AnalysisResultDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
