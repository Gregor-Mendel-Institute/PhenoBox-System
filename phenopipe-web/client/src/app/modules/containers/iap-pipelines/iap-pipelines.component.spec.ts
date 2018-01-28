import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { IapPipelinesComponent } from './iap-pipelines.component';

describe('IapPipelinesComponent', () => {
  let component: IapPipelinesComponent;
  let fixture: ComponentFixture<IapPipelinesComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ IapPipelinesComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(IapPipelinesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
