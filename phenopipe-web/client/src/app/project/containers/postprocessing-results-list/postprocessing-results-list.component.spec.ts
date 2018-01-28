import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PostprocessingResultsListComponent } from './postprocessing-results-list.component';

describe('PostprocessingResultsListComponent', () => {
  let component: PostprocessingResultsListComponent;
  let fixture: ComponentFixture<PostprocessingResultsListComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PostprocessingResultsListComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PostprocessingResultsListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
