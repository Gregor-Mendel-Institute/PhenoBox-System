import {Component, Input, OnInit, ViewChild} from '@angular/core';

@Component({
  selector: 'app-postprocessing-stacks-table',
  templateUrl: './postprocessing-stacks-table.component.html',
  styleUrls: ['./postprocessing-stacks-table.component.css']
})
export class PostprocessingStacksTableComponent implements OnInit {

  @Input()
  postprocessingStacks: GQL.IPostprocessingStackEdge[] = [];
  @ViewChild('stacksTable') table: any;
  expanded: any = {};
  constructor() { }

  ngOnInit() {
    console.log(this.postprocessingStacks);
  }

  toggleExpandRow(row) {
    console.log('Toggled Expand Row!', row);
    this.table.rowDetail.toggleExpandRow(row);
  }


  onDetailToggle(event) {
    console.log('Detail Toggled', event);
  }
}
