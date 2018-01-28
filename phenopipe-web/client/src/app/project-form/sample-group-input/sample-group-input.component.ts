import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {FormGroup} from '@angular/forms';

export interface AddSampleGroupEvent {
  name: string;
  treatment: string;
  isControl :boolean;
  sampleCount: number;
}

@Component({
  selector   : 'app-sample-group-input',
  templateUrl: './sample-group-input.component.html',
  styleUrls  : ['./sample-group-input.component.css']
})
export class SampleGroupInputComponent implements OnInit {

  @Input()
  parent: FormGroup;

  private _self: FormGroup;
  @Output()
  added: EventEmitter<AddSampleGroupEvent> = new EventEmitter<AddSampleGroupEvent>();

  constructor() {
  }

  ngOnInit() {
    this._self = <FormGroup>this.parent.get('sampleGroupDetails');
  }

  private onAdd(event) {
    this.added.emit(
      {
        name: this._self.get('sampleGroupNameInput').value,
        treatment: this._self.get('treatmentInput').value,
        isControl: this._self.get('isControlGroupInput').value,
        sampleCount: this._self.get('sampleCount').value
      })
    ;
    this._self.get('sampleGroupNameInput').setValue('');
    this._self.get('treatmentInput').setValue('');
    this._self.get('isControlGroupInput').setValue(false);
  }

}
