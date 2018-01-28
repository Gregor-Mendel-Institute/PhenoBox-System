import {Injectable} from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';

@Injectable()
export class FileUploadService {


  constructor(private http: HttpClient) {
  }

  postWithFile(endpoint: string, postData: any, files: File[] | FileList, fileMeta: { [key: string]: string }[]) {
    let headers = new HttpHeaders();
    let formData: FormData = new FormData();
    console.log(files);
    for (let i = 0; i < files.length; i++) {
      console.log(files[i].name);
      formData.append('files[]', files[i]);
    }
    if (fileMeta != null) {
      for (let i = 0; i < files.length; i++) {
        formData.append('fileMeta[]', JSON.stringify(fileMeta[i]));
      }
    }
    console.log('files[]', formData.get('files[]'));
    console.log('fileMeta[]', formData.get('fileMeta[]'));
    if (postData !== "" && postData !== undefined && postData !== null) {
      for (let property in postData) {
        if (postData.hasOwnProperty(property)) {
          formData.append(property, postData[property]);
        }
      }
    }
    console.log('details', formData.get('details'));
    return new Promise((resolve, reject) => {
      this.http.post(endpoint, formData, {
        headers: headers
      }).subscribe(
        res => {
          resolve(res);
        },
        error => {
          reject(error);
        }
      );
    });
  }
}
