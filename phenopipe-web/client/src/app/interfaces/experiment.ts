import {SampleGroup} from './sample-group';
export interface Experiment {
  id: string;
  name: string;
  groupName?: string;
  description?: string;
  scientist?: string;
  sampleGroups?: SampleGroup[];
}
