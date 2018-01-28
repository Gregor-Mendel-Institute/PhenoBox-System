import {Routes} from '@angular/router';
import {AuthGuard} from '../login/auth-guard.service';
import {ExperimentAnalysisComponent} from './containers/experiment-analysis/experiment-analysis.component';
import {TimestampAnalysisComponent} from './containers/timestamp-analysis/timestamp-analysis.component';
import {AnalysisDashboardComponent} from './containers/analysis-dashboard/analysis-dashboard.component';
import {PostprocessingDashboardComponent} from './containers/postprocessing-dashboard/postprocessing-dashboard.component';
import {AnalysisPostprocessingComponent} from './containers/analysis-postprocessing/analysis-postprocessing.component';
import {PostprocessingLogViewComponent} from './containers/postprocessing-log-view/postprocessing-log-view.component';
import {AnalysisLogViewComponent} from './containers/analysis-log-view/analysis-log-view.component';

export const analysisRoutes: Routes = [
  {
    path       : 'analysis',
    component  : AnalysisDashboardComponent,
    canActivate: [AuthGuard]
  },
  {
    path       : 'postprocessing',
    component  : PostprocessingDashboardComponent,
    canActivate: [AuthGuard]
  },
  {
    path       : 'postprocessing/log/:status_id',
    component  : PostprocessingLogViewComponent,
    canActivate: [AuthGuard]
  },
  {
    path       : 'postprocessing/:experiment_id/:analysis_id',
    component  : AnalysisPostprocessingComponent,
    canActivate: [AuthGuard]
  },
  {
    path       : 'analysis/:experiment_id',
    component  : ExperimentAnalysisComponent,
    canActivate: [AuthGuard]
  },
  {
    path       : 'analysis/log/:status_id',
    component  : AnalysisLogViewComponent,
    canActivate: [AuthGuard]
  },
  {
    path       : 'analysis/:experiment_id/:timestamp_id',
    component  : TimestampAnalysisComponent,
    canActivate: [AuthGuard]
  },

];
