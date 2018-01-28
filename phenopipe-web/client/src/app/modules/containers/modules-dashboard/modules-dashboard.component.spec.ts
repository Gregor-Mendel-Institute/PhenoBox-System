import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ModulesDashboardComponent } from './modules-dashboard.component';

describe('ModulesDashboardComponent', () => {
  let component: ModulesDashboardComponent;
  let fixture: ComponentFixture<ModulesDashboardComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ModulesDashboardComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ModulesDashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
