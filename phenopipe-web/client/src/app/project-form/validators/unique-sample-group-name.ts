import {FormArray, FormControl} from '@angular/forms';
import * as _ from 'lodash';

export const uniqueSampleGroupName = (formArray: FormArray): { [key: string]: boolean } => {
  let invalidControlPairs: Array<{ c1: FormControl; c2: FormControl }> = [];
  let uniq = _.uniqWith(formArray.controls, (c1: FormControl, c2: FormControl) => {
    let ret = c1.get('sampleGroupName').value === c2.get('sampleGroupName').value;
    if (ret) {
      invalidControlPairs.push({c1: c1, c2: c2});
    } else {
      let c1errs = c1.get('sampleGroupName').errors;
      let c2errs = c2.get('sampleGroupName').errors;
      //Preserve all other errors
      _.unset(c1errs, 'notUnique');
      _.unset(c2errs, 'notUnique');
      c1.get('sampleGroupName').setErrors((_.keys(c1errs).length === 0) ? null : c1errs);
      c2.get('sampleGroupName').setErrors((_.keys(c2errs).length === 0) ? null : c2errs);
    }
    return ret;
  });
  invalidControlPairs.forEach((pair) => {
    let c1err = pair.c1.get('sampleGroupName').errors;
    let c2err = pair.c2.get('sampleGroupName').errors;
    //Preserve other errors
    if (c1err !== null) {
      c1err['notUnique'] = true;
    } else {
      c1err = {notUnique: true}
    }
    if (c2err !== null) {
      c2err['notUnique'] = true;
    } else {
      c2err = {notUnique: true}
    }
    pair.c1.get('sampleGroupName').setErrors(c1err);
    pair.c2.get('sampleGroupName').setErrors(c2err);
  });
  return uniq.length === formArray.controls.length ? null : {notUnique: true};
};
