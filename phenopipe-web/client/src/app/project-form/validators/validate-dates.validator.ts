import {AbstractControl} from '@angular/forms';
import * as moment from 'moment';

export const validateDates = (control: AbstractControl): { [key: string]: boolean } => {
  let startDate = moment.utc(control.get('startDate').value).local();
  let startExpVal = control.get('startOfExperimentation').value;
  if (!startExpVal) {
    return null;
  }
  let startExp = moment.utc(startExpVal).local();
  if (startExp.isSameOrAfter(startDate)) {
    return null;
  } else {
    return {invalidDate: true};
  }
};
