import {Component, ElementRef, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {TemplateUtilsService} from '../../../shared/template-utils.service';

@Component({
  selector   : 'app-status-log-viewer',
  templateUrl: './status-log-viewer.component.html',
  styleUrls  : ['./status-log-viewer.component.css']
})
export class StatusLogViewerComponent implements OnInit {

  readonly headerHeight = 50;
  readonly rowHeight = 50;
  readonly pageLimit = 20;

  @Input()
  statusLogEntries: GQL.IStatusLogEntryEdge[];
  @Output()
  fetchMoreEntries: EventEmitter<number> = new EventEmitter<number>();

  constructor(private templateUtils: TemplateUtilsService, private el: ElementRef) {
  }

  ngOnInit() {
  }

  onScroll(offsetY: number) {
    // total height of all rows in the viewport
    const viewHeight = this.el.nativeElement.getBoundingClientRect().height - this.headerHeight;
    // check if we scrolled to the end of the viewport
    if (offsetY + viewHeight + 4 * this.rowHeight >= this.statusLogEntries.length * this.rowHeight) {
      // total number of results to load
      let limit = this.pageLimit;
      // check if we haven't fetched any results yet
      if (this.statusLogEntries.length === 0) {
        // calculate the number of rows that fit within viewport
        const pageSize = Math.ceil(viewHeight / this.rowHeight);
        // change the limit to pageSize such that we fill the first page entirely
        // (otherwise, we won't be able to scroll past it)
        limit = Math.max(pageSize, this.pageLimit);
      }
      this.fetchMoreEntries.emit(limit);
    }
  }
}
