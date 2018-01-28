import {Component, EventEmitter, Input, OnInit, Output, ViewChild} from '@angular/core';

@Component({
  selector   : 'app-task-status-table',
  templateUrl: './task-status-table.component.html',
  styleUrls  : ['./task-status-table.component.css']
})
export class TaskStatusTableComponent implements OnInit {

  @Input()
  taskStatus: GQL.ITaskStatusEdge[];
  @Output()
  detailToggled: EventEmitter<any> = new EventEmitter();//TODO type this
  @ViewChild('statusTable') table: any;


  columns = [
    {
      prop: 'node.name',
      name: 'Name',
    },
    {
      prop    : 'node.description',
      name    : 'Details',
      sortable: false,
      width   : 400
    },
    {
      prop: 'node.enqueuedAt',
      name: 'Enqueued at',
    },
    {
      prop: 'node.startedAt',
      name: 'Started at',
    },
    {
      prop: 'node.finishedAt',
      name: 'Finished at',
    }
  ];

  constructor() {
  }

  ngOnInit() {
  }

  toggleExpandRow(row) {
    this.table.rowDetail.toggleExpandRow(row);
  }

  onDetailToggle(event) {
    this.detailToggled.emit(event);
  }
}
