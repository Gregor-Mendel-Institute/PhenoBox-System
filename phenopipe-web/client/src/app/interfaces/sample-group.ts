import {Plant} from './plant';
export interface SampleGroup {

  id: string;
  name: string;
  sampleCount:number;
  description?: string;
  plants?: Plant[];
}

