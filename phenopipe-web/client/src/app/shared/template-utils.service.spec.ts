/* tslint:disable:no-unused-variable */

import { TestBed, async, inject } from '@angular/core/testing';
import { TemplateUtilsService } from './template-utils.service';

describe('TemplateUtilsService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [TemplateUtilsService]
    });
  });

  it('should ...', inject([TemplateUtilsService], (service: TemplateUtilsService) => {
    expect(service).toBeTruthy();
  }));
});
