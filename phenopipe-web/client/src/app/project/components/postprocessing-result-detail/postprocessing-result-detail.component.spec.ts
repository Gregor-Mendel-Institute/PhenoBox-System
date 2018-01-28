import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {PostprocessingResultDetailComponent} from './postprocessing-result-detail.component';

describe('PostprocessingResultDetailComponent', () => {
  let component: PostprocessingResultDetailComponent;
  let fixture: ComponentFixture<PostprocessingResultDetailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [PostprocessingResultDetailComponent]
    })
      .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PostprocessingResultDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
