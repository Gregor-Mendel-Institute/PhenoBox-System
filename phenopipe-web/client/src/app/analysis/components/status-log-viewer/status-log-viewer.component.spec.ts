import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { StatusLogViewerComponent } from './status-log-viewer.component';

describe('StatusLogViewerComponent', () => {
  let component: StatusLogViewerComponent;
  let fixture: ComponentFixture<StatusLogViewerComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ StatusLogViewerComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(StatusLogViewerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
