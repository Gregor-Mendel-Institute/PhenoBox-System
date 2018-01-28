import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {Form, FormArray, FormGroup} from '@angular/forms';
import {PlantCountChangedEvent} from '../sample-group/sample-group.component';

export interface RemoveSampleGroupEvent{
  index:number;
}

@Component({
  selector: 'app-sample-group-list',
  templateUrl: './sample-group-list.component.html',
  styleUrls: ['./sample-group-list.component.css']
})
export class SampleGroupListComponent implements OnInit {

  @Input()
  parent: FormGroup;
  @Input()
  restricted:boolean;
  @Output()
  plantCountChanged:EventEmitter<PlantCountChangedEvent> = new EventEmitter<PlantCountChangedEvent>();
  @Output()
  removeSampleGroup:EventEmitter<RemoveSampleGroupEvent> = new EventEmitter<RemoveSampleGroupEvent>();
  private self: FormArray;

  constructor() { }

  ngOnInit() {
    this.self = <FormArray>this.parent.get('sampleGroups')
  }

  onPlantCountChanged(event:PlantCountChangedEvent){
    this.plantCountChanged.emit(event);
  }

  onRemoveSampleGroup(index:number){
    this.removeSampleGroup.emit({index:index});
  }
}
