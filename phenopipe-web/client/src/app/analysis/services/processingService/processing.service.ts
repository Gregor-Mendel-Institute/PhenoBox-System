import {Injectable} from '@angular/core';
import {environment} from '../../../../environments/environment';
import {HttpClient} from '@angular/common/http';

@Injectable()
export class ProcessingService {

  constructor(private http: HttpClient) {
  }

  invokeAnalysis(timestampId: string, pipelineId: string, stackIds: string[] = [], note: string = '') {
    let payload = {
      timestamp_id            : timestampId,
      pipeline_id             : pipelineId,
      postprocessing_stack_ids: stackIds,
      note                    : note
    };
    return this.http.post(environment.iapAnalysisEndpoint, payload);
  }

  invokePostprocess(analysisId: string, stackIds: string[], note: string = '') {
    let payload = {
      analysis_id             : analysisId,
      postprocessing_stack_ids: stackIds,
      note                    : note
    };
    return this.http.post(environment.postprocessingEndpoint, payload);
  }
}
