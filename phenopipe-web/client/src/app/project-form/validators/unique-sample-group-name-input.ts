import {FormControl, FormGroup, FormArray} from '@angular/forms';
import * as _ from 'lodash';
export const uniqueSampleGroupNameInput = (group: FormGroup): {[key: string]: boolean} => {
  let name = group.get('sampleGroupDetails').get('sampleGroupNameInput').value;
  if (name.trim() === '') {
    return null;
  }
  console.log(name);
  console.log((group.get('sampleGroups')));
  let index = _.findIndex((group.get('sampleGroups') as FormArray).controls, (c: FormControl) => {

    return c.get('sampleGroupName').value === name;
  });
  console.log(index);
  return index === -1 ? null : {notUnique: true};
};
