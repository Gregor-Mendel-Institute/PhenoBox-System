import {FormArray, FormControl} from '@angular/forms';
import * as _ from 'lodash';

export const singleControlGroup = (formArray: FormArray): { [key: string]: boolean } => {
  let invalidControlPairs: Array<{ c1: FormControl; c2: FormControl }> = [];
  let uniq = _.uniqWith(formArray.controls, (c1: FormControl, c2: FormControl) => {
    let ret = c1.get('isControl').value === c2.get('isControl').value;
    if (ret) {
      invalidControlPairs.push({c1: c1, c2: c2});
    } else {
      let c1errs = c1.get('isControl').errors;
      let c2errs = c2.get('isControl').errors;
      //Preserve all other errors
      _.unset(c1errs, 'multipleControlGroups');
      _.unset(c2errs, 'multipleControlGroups');
      c1.get('isControl').setErrors((_.keys(c1errs).length === 0) ? null : c1errs);
      c2.get('isControl').setErrors((_.keys(c2errs).length === 0) ? null : c2errs);
    }
    return ret;
  });
  invalidControlPairs.forEach((pair) => {
    let c1err = pair.c1.get('isControl').errors;
    let c2err = pair.c2.get('isControl').errors;
    //Preserve other errors
    if (c1err !== null) {
      c1err['multipleControlGroups'] = true;
    } else {
      c1err = {multipleControlGroups: true}
    }
    if (c2err !== null) {
      c2err['multipleControlGroups'] = true;
    } else {
      c2err = {multipleControlGroups: true}
    }
    pair.c1.get('isControl').setErrors(c1err);
    pair.c2.get('isControl').setErrors(c2err);
  });
  return uniq.length === formArray.controls.length ? null : {multipleControlGroups: true};
};
