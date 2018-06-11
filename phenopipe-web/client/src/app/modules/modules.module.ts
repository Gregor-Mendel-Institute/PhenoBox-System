import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {ModulesDashboardComponent,} from './containers/modules-dashboard/modules-dashboard.component';
import {RouterModule} from '@angular/router';
import {modulesRoutes} from './modules.routes';
import {IapPipelinesComponent} from './containers/iap-pipelines/iap-pipelines.component';
import {PostprocessingStacksComponent} from './containers/postprocessing-stacks/postprocessing-stacks.component';
import {PostprocessingStackUploadFormComponent} from './containers/postprocessing-stack-upload-form/postprocessing-stack-upload-form.component';
import {ReactiveFormsModule} from '@angular/forms';
import {SharedModule} from '../shared/shared.module';
import {ScriptListComponent} from './containers/postprocessing-stack-upload-form/script-list/script-list.component';
import {ScriptComponent} from './containers/postprocessing-stack-upload-form/script/script.component';
import {TabsModule} from 'ngx-bootstrap';
import {IapPipelineUploadFormComponent} from './containers/iap-pipeline-upload-form/iap-pipeline-upload-form.component';
import {NgxDatatableModule} from '@swimlane/ngx-datatable';
import {FileUploadService} from './file-upload.service';
import {HttpClientModule} from '@angular/common/http';

@NgModule({
  imports     : [
    CommonModule,
    ReactiveFormsModule,
    HttpClientModule,
    SharedModule,
    RouterModule.forChild(modulesRoutes),
    TabsModule.forRoot(),
    NgxDatatableModule
  ],
  declarations: [
    ModulesDashboardComponent,
    IapPipelinesComponent,
    PostprocessingStacksComponent,
    PostprocessingStackUploadFormComponent,
    ScriptListComponent,
    ScriptComponent,
    IapPipelineUploadFormComponent,

  ],
  providers   : [
    FileUploadService
  ],
  exports     : [ModulesDashboardComponent]
})
export class ModulesModule {
}
