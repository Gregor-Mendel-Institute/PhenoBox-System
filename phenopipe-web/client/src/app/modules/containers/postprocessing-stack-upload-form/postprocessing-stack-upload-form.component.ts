import {Component, OnInit, ViewChild} from '@angular/core';
import {FormArray, FormBuilder, FormGroup, Validators} from '@angular/forms';
import {FileUploadService} from '../../file-upload.service';
import {environment} from "environments/environment";
import {AuthService} from '../../../login/auth.service';
import {ToastrService} from 'ngx-toastr';

interface Script {
  name: string;
  description: string;
  script: File;
}

@Component({
  selector   : 'app-postprocessing-stack-upload-form',
  templateUrl: './postprocessing-stack-upload-form.component.html',
  styleUrls  : ['./postprocessing-stack-upload-form.component.css']
})
export class PostprocessingStackUploadFormComponent implements OnInit {

  @ViewChild('fileInput') fileInput;
  @ViewChild('addScriptBtn') addScriptBtn;
  private stack: FormGroup;

  private selectedScriptIndex: number = -1;
  private disableAddScripts: boolean = true;
  private username: string;
  private error: { status: number; details: { [key: string]: string }; };

  constructor(private auth: AuthService, private toastr:ToastrService, private fb: FormBuilder, private uploadService: FileUploadService) {
  }

  ngOnInit() {
    this.username = this.auth.getUsername();
    let scientistName = this.auth.getFullName();
    let scripts: FormGroup[] = [];
    this.stack = this.fb.group({
      details: this.fb.group({
        name       : ['', [Validators.required]],//TODO add unique validator
        description: [''],
        author     : [{value: scientistName, disabled: true}, Validators.required]
      }),
      scripts: this.fb.array(scripts)//TODO add unique script name validator
    });
    this.addScriptBtn.nativeElement.disabled = true;
  }

  private createScript(script: Script): FormGroup {

    return this.fb.group({
      name       : [script.name, [Validators.required]],
      description: [script.description],
      script     : [script.script]
    });
  }

  private scriptSelected($event) {
    //Set it to -1 to force destruction of Script component
    //Otherwise the form data would not be reloaded
    //FIXME use no workaround
    this.selectedScriptIndex = -1;
    setTimeout(() => {
      this.selectedScriptIndex = $event
    });
  }

  fileChanged($event) {
    this.disableAddScripts = $event.target.files.length <= 0;
  }

  addScripts($event) {
    let files: FileList = this.fileInput.nativeElement.files;
    if (files.length > 0) {
      let selectIndex = this.stack.get('scripts')['controls'].length;
      for (let i = 0; i < files.length; i++) {
        let name = files[i].name.substring(0, files[i].name.length - 2);
        (<FormArray>this.stack.get('scripts')).push(
          this.createScript({name: name, description: '', script: files[i]}))
      }
      this.scriptSelected(selectIndex);
    }
    this.fileInput.nativeElement.value = '';
    this.disableAddScripts = true;
  }

  private onSubmit() {
    this.error = null;
    let files: File[] = [];
    this.stack.get('scripts')['controls'].forEach((control) => {
      files.push(control.value.script);
    });
    console.log(this.stack.getRawValue());
    let data = {
      name       : this.stack.get('details.name').value,
      description: this.stack.get('details.description').value,
      author     : this.username,
    };
    this.uploadService.postWithFile(environment.uploadPostprocessingStackEndpoint, data,
      files, this.stack.get('scripts').value).then(
      (val) => {
        this.fileInput.nativeElement.value = '';
        this.stack.reset();
        this.selectedScriptIndex = -1;
        this.stack.setControl('scripts', this.fb.array([]));
        this.stack.get('details.author').setValue(this.auth.getFullName());
        this.toastr.success("Postprocessing stack uploaded successfully");
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
