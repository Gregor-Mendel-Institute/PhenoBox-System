import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PostprocessingDashboardComponent } from './postprocessing-dashboard.component';

describe('PostprocessingDashboardComponent', () => {
  let component: PostprocessingDashboardComponent;
  let fixture: ComponentFixture<PostprocessingDashboardComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PostprocessingDashboardComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PostprocessingDashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
