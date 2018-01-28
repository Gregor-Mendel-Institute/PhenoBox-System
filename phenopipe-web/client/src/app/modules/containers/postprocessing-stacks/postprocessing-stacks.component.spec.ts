import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PostprocessingStacksComponent } from './postprocessing-stacks.component';

describe('PostprocessingStacksComponent', () => {
  let component: PostprocessingStacksComponent;
  let fixture: ComponentFixture<PostprocessingStacksComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PostprocessingStacksComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PostprocessingStacksComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
