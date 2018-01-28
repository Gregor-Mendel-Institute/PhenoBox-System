import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';

@Component({
  selector   : 'app-snapshot-detail',
  templateUrl: './snapshot-detail.component.html',
  styleUrls  : ['./snapshot-detail.component.css']
})
export class SnapshotDetailComponent implements OnInit {
  @Input()
  viewOnly: boolean;
  @Input()
  snapshot: GQL.ISnapshotEdge;
  @Input()
  allowExclusion: boolean = true;
  @Output()
  onDeleteSnapshot: EventEmitter<GQL.ISnapshot> = new EventEmitter<GQL.ISnapshot>();
  @Output()
  onChangeSnapshotExclusion: EventEmitter<{ snapshot: GQL.ISnapshot; exclude: boolean }> = new EventEmitter<{ snapshot: GQL.ISnapshot; exclude: boolean }>();

  constructor() {
  }

  ngOnInit() {
  }

  deleteSnapshot(event) {
    if (!this.viewOnly) {
      this.onDeleteSnapshot.emit(this.snapshot.node);
    }
  }

  excludeSnapshot(event) {
    if (this.allowExclusion) {
      this.onChangeSnapshotExclusion.emit({snapshot: this.snapshot.node, exclude: true});
    }
  }

  includeSnapshot(event) {
    if (this.allowExclusion) {
      this.onChangeSnapshotExclusion.emit({snapshot: this.snapshot.node, exclude: false});
    }
  }
}
