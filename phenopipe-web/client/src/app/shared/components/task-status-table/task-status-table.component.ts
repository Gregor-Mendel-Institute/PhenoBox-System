import {Component, EventEmitter, Input, OnInit, Output, ViewChild} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';

@Component({
  selector   : 'app-task-status-table',
  templateUrl: './task-status-table.component.html',
  styleUrls  : ['./task-status-table.component.css']
})
export class TaskStatusTableComponent implements OnInit {

  @Input()
  taskStatus: GQL.ITaskEdge[];
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

  constructor(private activatedRoute: ActivatedRoute, private router: Router) {
  }

  ngOnInit() {
  }

  toggleExpandRow(row) {
    this.table.rowDetail.toggleExpandRow(row);
  }

  onDetailToggle(event) {
    this.detailToggled.emit(event);
  }

  openLog(task) {
    console.log(task);
    this.router.navigate(['log', task.id],
      {relativeTo: this.activatedRoute, queryParams: {'job_ids': task.jobs.edges.map(job => job.node.id)}})
  }
}
