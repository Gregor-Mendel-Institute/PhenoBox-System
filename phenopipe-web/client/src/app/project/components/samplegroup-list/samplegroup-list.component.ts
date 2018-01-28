import {Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges} from '@angular/core';
import * as _ from 'lodash';
import {ChangeSnapshotExclusionEvent, DeleteSnapshotEvent} from '../group-detail/group-detail.component';

@Component({
  selector   : 'app-samplegroup-list',
  templateUrl: './samplegroup-list.component.html',
  styleUrls  : ['./samplegroup-list.component.css']
})
export class SamplegroupListComponent implements OnInit, OnChanges {

  @Input()
  sampleGroups: GQL.ISampleGroupEdge[] = [];
  @Input()
  printable: boolean;
  @Input()
  viewOnly: boolean;
  @Input()
  allowSnapshotExclusion: boolean = true;
  @Output()
  printGroup: EventEmitter<GQL.ISampleGroup> = new EventEmitter<GQL.ISampleGroup>();
  @Output()
  onDeleteSnapshot: EventEmitter<DeleteSnapshotEvent> = new EventEmitter<DeleteSnapshotEvent>();
  @Output()
  onChangeSnapshotExclusion: EventEmitter<ChangeSnapshotExclusionEvent> = new EventEmitter<ChangeSnapshotExclusionEvent>();


  private accordionState: boolean [] = [];

  constructor() {
  }

  ngOnInit() {

  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['sampleGroups'] && changes['sampleGroups'].currentValue) {
      //FIXME Needed until deleting empty sample groups works on snapshot delete
      this.sampleGroups = this.sampleGroups.filter((group) => group.node.plants.edges.length > 0);

      if (this.sampleGroups.length != this.accordionState.length) {
        this.accordionState = Array(this.sampleGroups.length);
        _.fill(this.accordionState, false, 0, this.accordionState.length);
        //this.accordionState[0] = true;
      }
    }
  }

  deleteSnapshot(event: DeleteSnapshotEvent) {
    this.onDeleteSnapshot.emit(event);
  }

  changeSnapshotExclusion(event: ChangeSnapshotExclusionEvent) {
    console.log(this.accordionState);
    this.onChangeSnapshotExclusion.emit(event);
  }

  private printGroupClicked(group: GQL.ISampleGroup, index: number) {
    if (this.printable) {
      this.accordionState[index] = !this.accordionState[index];
      this.printGroup.emit(group);
      //this.groupToPrint = this.experiment.sampleGroups['edges'][index].node;
      //this.groupModal.show();
    }
  }

}
