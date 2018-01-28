import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {TextareaAutosizeDirective} from './textarea-autosize.directive';
import {DndModule} from 'ng2-dnd';
import {PostprocessingStacksTableComponent} from './components/postprocessing-stacks-table/postprocessing-stacks-table.component';
import {NgxDatatableModule} from '@swimlane/ngx-datatable';
import {TaskStatusTableComponent} from './components/task-status-table/task-status-table.component';
import {DownloadService} from './download-results-service/download-results.service';
import {TemplateUtilsService} from './template-utils.service';
import {AlertComponent, AlertModule} from 'ngx-bootstrap';
import {RouterModule} from '@angular/router';

@NgModule({
  imports     : [
    CommonModule,
    DndModule.forRoot(),
    AlertModule.forRoot(),
    NgxDatatableModule,
    RouterModule.forChild([])
  ],
  providers   : [DownloadService, TemplateUtilsService,],
  declarations: [TextareaAutosizeDirective, PostprocessingStacksTableComponent, TaskStatusTableComponent],
  exports     : [
    TextareaAutosizeDirective,
    DndModule,
    AlertComponent,
    PostprocessingStacksTableComponent,
    TaskStatusTableComponent
  ]
})
export class SharedModule {
}
