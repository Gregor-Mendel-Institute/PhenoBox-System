import {Injectable} from '@angular/core';
import * as moment from 'moment';

@Injectable()
export class TemplateUtilsService {

  constructor() {
  }

  formatTime(timestamp, format) {
    if (!timestamp) {
      return '';
    }
    let loc = moment.utc(timestamp).local();
    return moment(loc).format(format);
    /*if (excludeTime) {
      return moment(loc).format('YYYY-MM-DD');
    } else {
      return moment(loc).format('YYYY-MM-DD HH:mm');
    }*/
  }
}
