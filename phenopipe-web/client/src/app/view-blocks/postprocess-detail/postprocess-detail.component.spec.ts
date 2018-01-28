import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PostprocessDetailComponent } from './postprocess-detail.component';

describe('PostprocessDetailComponent', () => {
  let component: PostprocessDetailComponent;
  let fixture: ComponentFixture<PostprocessDetailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PostprocessDetailComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PostprocessDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
