import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { StackSelectorComponent } from './stack-selector.component';

describe('StackSelectorComponent', () => {
  let component: StackSelectorComponent;
  let fixture: ComponentFixture<StackSelectorComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ StackSelectorComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(StackSelectorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
