import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import * as _ from 'lodash';

export interface DeleteSnapshotEvent {
  snapshotId: string;
  plantId: string;
  groupId: string;
}

export interface ChangeSnapshotExclusionEvent {
  snapshotId: string;
  plantId: string;
  groupId: string;
  exclude: boolean;
}

@Component({
  selector   : 'app-group-detail',
  templateUrl: './group-detail.component.html',
  styleUrls  : ['./group-detail.component.css']
})
export class GroupDetailComponent implements OnInit {

  @Input()
  viewOnly: boolean;
  @Input()
  allowSnapshotExclusion: boolean = true;

  @Input('group')
  set group(value: GQL.ISampleGroup) {

    this._group = value;
    console.log(this._group);
    this.sortedPlants = _.sortBy(this._group.plants.edges, elem => elem.node.index);
  }

  @Output()
  onDeleteSnapshot: EventEmitter<DeleteSnapshotEvent> = new EventEmitter<DeleteSnapshotEvent>();
  @Output()
  onChangeSnapshotExclusion: EventEmitter<ChangeSnapshotExclusionEvent> = new EventEmitter<ChangeSnapshotExclusionEvent>();


  _group: GQL.ISampleGroup;
  sortedPlants: GQL.IPlantEdge[];
  indices: number[];

  constructor() {
  }

  ngOnInit() {
    this.indices = Array(Math.ceil(this.sortedPlants.length / 2)).fill(0).map((x, i) => i * 2);
  }

  deleteSnapshot(snapshot: GQL.ISnapshot, plant: GQL.IPlant) {
    this.onDeleteSnapshot.emit({snapshotId: snapshot.id, plantId: plant.id, groupId: this._group.id});
  }

  changeSnapshotExclusion(event: { snapshot: GQL.ISnapshot, exclude: boolean; }, plant: GQL.IPlant) {
    console.log('exclusion changed');
    this.onChangeSnapshotExclusion.emit(
      {snapshotId: event.snapshot.id, plantId: plant.id, groupId: this._group.id, exclude: event.exclude});
  }


}
