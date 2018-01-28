import {Component, OnInit, ViewChild} from '@angular/core';
import {environment} from '../../../../environments/environment';
import {FileUploadService} from '../../file-upload.service';
import {ToastrService} from 'ngx-toastr';

@Component({
  selector   : 'app-iap-pipeline-upload-form',
  templateUrl: './iap-pipeline-upload-form.component.html',
  styleUrls  : ['./iap-pipeline-upload-form.component.css']
})
export class IapPipelineUploadFormComponent implements OnInit {

  @ViewChild('fileInput') fileInput;

  private valid: boolean;

  constructor(private uploadService: FileUploadService, private toastr: ToastrService) {
  }

  ngOnInit() {
  }

  fileChanged($event) {
    //TODO Check if this pipeline already exists

  }

  uploadPipeline($event) {
    let files: FileList = this.fileInput.nativeElement.files;
    if (files.length > 0) {
      this.uploadService.postWithFile(environment.uploadIapPipelineEndpoint, null,
        files, null).then(
        (val) => {
          this.toastr.success("Pipeline uploaded successfully");
          this.fileInput.nativeElement.value = '';
        },
        (err) => {
          if (err.status == 409 || err.status == 422) {
            this.toastr.error(err.error.msg)
          } else if (err.status == 503) {
            this.toastr.error('The Service is currently unavailable. Please try again later.')
          } else if (err.status == 500) {
            this.toastr.error('Internal Server error. If this error keeps occuring please contact an administrator.')
          }
        }
      );
    }
  }
}
