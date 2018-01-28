import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AnalysisPostprocessingComponent } from './analysis-postprocessing.component';

describe('AnalysisPostprocessingComponent', () => {
  let component: AnalysisPostprocessingComponent;
  let fixture: ComponentFixture<AnalysisPostprocessingComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AnalysisPostprocessingComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AnalysisPostprocessingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
