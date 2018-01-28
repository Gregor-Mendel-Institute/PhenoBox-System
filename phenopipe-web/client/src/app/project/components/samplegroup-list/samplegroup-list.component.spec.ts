import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SamplegroupListComponent } from './samplegroup-list.component';

describe('SamplegroupListComponent', () => {
  let component: SamplegroupListComponent;
  let fixture: ComponentFixture<SamplegroupListComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SamplegroupListComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SamplegroupListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
