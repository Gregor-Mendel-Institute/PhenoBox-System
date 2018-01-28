import {Routes} from '@angular/router';
import {ModulesDashboardComponent} from './containers/modules-dashboard/modules-dashboard.component';
import {AuthGuard} from '../login/auth-guard.service';
import {IapPipelinesComponent} from './containers/iap-pipelines/iap-pipelines.component';
import {PostprocessingStacksComponent} from './containers/postprocessing-stacks/postprocessing-stacks.component';
import {IapPipelineUploadFormComponent} from './containers/iap-pipeline-upload-form/iap-pipeline-upload-form.component';
import {PostprocessingStackUploadFormComponent} from './containers/postprocessing-stack-upload-form/postprocessing-stack-upload-form.component';

export const modulesRoutes: Routes = [
  {
    path     : 'modules',
    component: ModulesDashboardComponent,
    children : [
      {
        path:'',
        redirectTo:'iap-pipelines',
        pathMatch:'full'
      },
      {
        path       : 'iap-pipelines',
        component  : IapPipelinesComponent,
        canActivate: [AuthGuard]
      },
      {
        path       : 'iap-pipelines/upload',
        component  : IapPipelineUploadFormComponent,
        canActivate: [AuthGuard]
      },
      {
        path       : 'postprocessing-stacks',
        component  : PostprocessingStacksComponent,
        canActivate: [AuthGuard]
      },
      {
        path       : 'postprocessing-stacks/upload',
        component  : PostprocessingStackUploadFormComponent,
        canActivate: [AuthGuard]
      }
    ]
  }
];
