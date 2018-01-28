import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PostprocessingStackUploadFormComponent } from './postprocessing-stack-upload-form.component';

describe('PostprocessingStackUploadFormComponent', () => {
  let component: PostprocessingStackUploadFormComponent;
  let fixture: ComponentFixture<PostprocessingStackUploadFormComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PostprocessingStackUploadFormComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PostprocessingStackUploadFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
