import {ProjectDashboardComponent} from './project/containers/project-dashboard/project-dashboard.component';
import {LoginComponent} from './login/login.component';
import {Routes} from '@angular/router';
import {ProjectDetailComponent} from './project/containers/project-detail/project-detail.component';
import {PageNotFoundComponent} from './page-not-found/page-not-found.component';
import {ExperimentsResolve} from './project/containers/project-dashboard/experiments-resolve';
import {ExperimentResolve} from './project/containers/project-detail/experiment-resolve';
import {AuthGuard} from './login/auth-guard.service';
import {CreateProjectComponent} from './project/containers/create-project/create-project.component';
import {EditProjectComponent} from './project/containers/edit-project/edit-project.component';
import {TimestampDetailComponent} from './project/containers/timestamp-detail/timestamp-detail.component';
import {TimestampDetailResolve} from './project/containers/timestamp-detail/timestamp-detail-resolve';
import {PostprocessingResultDetailComponent} from './project/components/postprocessing-result-detail/postprocessing-result-detail.component';
import {AnalysisResultDetailComponent} from './project/containers/analysis-result-detail/analysis-result-detail.component';

export const appRoutes: Routes = [
  {
    path      : '',
    redirectTo: 'login',
    pathMatch : 'full'
  },
  {
    path     : 'login',
    component: LoginComponent
  },
  {
    path       : 'create',
    component  : CreateProjectComponent,
    canActivate: [AuthGuard]
  },
  {
    path       : 'edit/:id',
    component  : EditProjectComponent,
    resolve    : {experiment: ExperimentResolve},
    canActivate: [AuthGuard]
  },
  {
    path       : 'projects',
    component  : ProjectDashboardComponent,
    resolve    : {experiments: ExperimentsResolve},
    canActivate: [AuthGuard],

  },
  {
    path       : 'projects/:id',
    component  : ProjectDetailComponent,
    resolve    : {experiment: ExperimentResolve},
    canActivate: [AuthGuard],
    children   : [
      {
        path       : ':timestamp_id',
        component  : TimestampDetailComponent,
        resolve    : {timestamp: TimestampDetailResolve},
        canActivate: [AuthGuard]
      }
    ]
  },
  {
    path       : 'results/:timestamp_id/:analysis_id',
    component  : AnalysisResultDetailComponent,
    canActivate: [AuthGuard]
  },
  {
    path       : 'results/:timestamp_id/:analysis_id/:postprocess_id',
    component  : PostprocessingResultDetailComponent,
    canActivate: [AuthGuard]
  },
  {
    path     : '**',
    component: PageNotFoundComponent
  }
];
