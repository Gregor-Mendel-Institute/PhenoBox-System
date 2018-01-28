import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PostprocessingStacksTableComponent } from './postprocessing-stacks-table.component';

describe('PostprocessingStacksTableComponent', () => {
  let component: PostprocessingStacksTableComponent;
  let fixture: ComponentFixture<PostprocessingStacksTableComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PostprocessingStacksTableComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PostprocessingStacksTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
