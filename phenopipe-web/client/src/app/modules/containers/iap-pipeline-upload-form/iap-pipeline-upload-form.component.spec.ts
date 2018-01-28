import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { IapPipelineUploadFormComponent } from './iap-pipeline-upload-form.component';

describe('IapPipelineUploadFormComponent', () => {
  let component: IapPipelineUploadFormComponent;
  let fixture: ComponentFixture<IapPipelineUploadFormComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ IapPipelineUploadFormComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(IapPipelineUploadFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
