import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PostprocessingLogViewComponent } from './postprocessing-log-view.component';

describe('PostprocessingLogViewComponent', () => {
  let component: PostprocessingLogViewComponent;
  let fixture: ComponentFixture<PostprocessingLogViewComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PostprocessingLogViewComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PostprocessingLogViewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
