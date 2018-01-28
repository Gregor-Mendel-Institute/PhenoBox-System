import {Injectable} from '@angular/core';
import {environment} from '../../../environments/environment';
import {saveAs} from 'file-saver';
import * as moment from 'moment';
import {HttpClient, HttpHeaders} from '@angular/common/http';

@Injectable()
export class DownloadService {

  constructor(private http: HttpClient) {

  }

  downloadResults(analysisId: string, withPictures: boolean) {
    const headers = new HttpHeaders()
      .set('Content-Type', 'application/json')
      .set('Accept', 'application/zip');
    return this.http.post(environment.downloadResultsEndpoint,
      {analysis_id: analysisId, with_pictures: withPictures},
      {headers: headers, responseType: 'blob', observe: 'response'}).map(
      data => this.saveToFileSystem(data))
  }

  downloadImages(timestampId: string) {
    const headers = new HttpHeaders()
      .set('Content-Type', 'application/json')
      .set('Accept', 'application/zip');


    return this.http.post(environment.downloadImagesEndpoint,
      {timestamp_id: timestampId}, {headers: headers, responseType: 'blob', observe: 'response'}).map(
      data => this.saveToFileSystem(data))

  }


  private saveToFileSystem(response) {
    const contentDispositionHeader: string = response.headers.get('content-disposition');
    const parts: string[] = contentDispositionHeader.split(';');
    const filename = parts[1].split('=')[1];
    let nameParts: string[] = filename.split('_');
    let time: string = nameParts[nameParts.length - 1].substring(0, nameParts[nameParts.length - 1].length - 4);
    nameParts[nameParts.length - 1] = moment(time).local().format('YYYY-MM-DD_HH-mm') + '.zip';
    const blob = response.body;
    const formatted_name = nameParts.join('_');
    saveAs(blob, formatted_name);
    return formatted_name;
  }


}
