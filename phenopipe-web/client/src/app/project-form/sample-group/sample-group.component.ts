import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {FormGroup} from '@angular/forms';

export interface PlantCountChangedEvent {
  formGroupName: string;
  oldCount: number;
  newCount: number;
}

@Component({
  selector   : 'sample-group',
  templateUrl: './sample-group.component.html',
  styleUrls  : ['./sample-group.component.css']
})
export class SampleGroupComponent implements OnInit {
  @Input() parent: FormGroup;
  @Input() formGrName: string;
  @Input() restricted: boolean;
  @Output() plantCountChanged: EventEmitter<PlantCountChangedEvent> = new EventEmitter<PlantCountChangedEvent>();
  private self: FormGroup;

  constructor() {
  }

  ngOnInit() {
    this.self = <FormGroup>this.parent.get('' + this.formGrName);
  }

  private setPlantCount() {
    if (!this.restricted) {
      let newCount = parseInt(this.self.get('plantCount').value, 10);
      let oldCount = this.self.get('plants').value.length;
      if (oldCount !== newCount) {
        this.plantCountChanged.emit({formGroupName: this.formGrName, oldCount: oldCount, newCount: newCount});
      }
    }
  }
}
