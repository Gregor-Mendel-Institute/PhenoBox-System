import { TestBed, inject } from '@angular/core/testing';

import { ProcessingService } from './processing.service';

describe('ProcessingService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ProcessingService]
    });
  });

  it('should be created', inject([ProcessingService], (service: ProcessingService) => {
    expect(service).toBeTruthy();
  }));
});
