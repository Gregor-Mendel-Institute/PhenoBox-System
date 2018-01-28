import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TaskStatusTableComponent } from './task-status-table.component';

describe('TaskStatusTableComponent', () => {
  let component: TaskStatusTableComponent;
  let fixture: ComponentFixture<TaskStatusTableComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TaskStatusTableComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TaskStatusTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
