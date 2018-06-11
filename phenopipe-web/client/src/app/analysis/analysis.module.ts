import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {SharedModule} from '../shared/shared.module';
import {RouterModule} from '@angular/router';
import {analysisRoutes} from './analysis.routes';
import {ExperimentAnalysisComponent} from './containers/experiment-analysis/experiment-analysis.component';
import {TimestampAnalysisComponent} from './containers/timestamp-analysis/timestamp-analysis.component';
import {AnalysisDashboardComponent} from './containers/analysis-dashboard/analysis-dashboard.component';
import {ReactiveFormsModule} from '@angular/forms';
import {NgxDatatableModule} from '@swimlane/ngx-datatable';
import {PostprocessingDashboardComponent} from './containers/postprocessing-dashboard/postprocessing-dashboard.component';
import {StackSelectorComponent} from './components/stack-selector/stack-selector.component';
import {AnalysisPostprocessingComponent} from './containers/analysis-postprocessing/analysis-postprocessing.component';
import {ProcessingService} from './services/processingService/processing.service';
import {ViewBlocksModule} from '../view-blocks/view-blocks.module';
import {StatusLogViewerComponent} from './components/status-log-viewer/status-log-viewer.component';
import {LogViewComponent} from './containers/log-view/log-view.component';

@NgModule({
  imports     : [
    CommonModule,
    ReactiveFormsModule,
    SharedModule,
    RouterModule.forChild(analysisRoutes),
    NgxDatatableModule,
    ViewBlocksModule
  ],
  providers   : [ProcessingService],
  declarations: [
    ExperimentAnalysisComponent,
    TimestampAnalysisComponent,
    AnalysisDashboardComponent,
    PostprocessingDashboardComponent,
    StackSelectorComponent,
    AnalysisPostprocessingComponent,
    StatusLogViewerComponent,
    LogViewComponent,
  ]
})
export class AnalysisModule {

}
