import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';
import {AppComponent} from './app.component';
import {Router, RouterModule} from '@angular/router';
import {ProjectFormComponent} from './project-form/project-form.component';
import {ProjectDashboardComponent} from './project/containers/project-dashboard/project-dashboard.component';
import {PageNotFoundComponent} from './page-not-found/page-not-found.component';
import {ReactiveFormsModule} from '@angular/forms';
import {PlantListComponent} from './project-form/plant-list/plant-list.component';
import {SampleGroupComponent} from './project-form/sample-group/sample-group.component';
import {CollapseModule} from 'ngx-bootstrap/collapse';
import {AccordionModule} from 'ngx-bootstrap/accordion';
import {Apollo, ApolloModule} from 'apollo-angular';
import {ExperimentsResolve} from './project/containers/project-dashboard/experiments-resolve';
import {ProjectDetailComponent} from './project/containers/project-detail/project-detail.component';
import {appRoutes} from './app.routes';
import {ExperimentResolve} from './project/containers/project-detail/experiment-resolve';
import {ModalModule} from 'ngx-bootstrap/modal';
import {LoginComponent} from './login/login.component';
import {AuthService} from './login/auth.service';
import {AuthGuard} from './login/auth-guard.service';
import {TooltipModule} from 'ngx-bootstrap';
import {CreateProjectComponent} from './project/containers/create-project/create-project.component';
import {EditProjectComponent} from './project/containers/edit-project/edit-project.component';
import {SampleGroupListComponent} from './project-form/sample-group-list/sample-group-list.component';
import {ProjectDetailsComponent} from './project-form/project-details/project-details.component';
import {SampleGroupInputComponent} from './project-form/sample-group-input/sample-group-input.component';
import {TimestampDetailComponent} from './project/containers/timestamp-detail/timestamp-detail.component';
import {GroupDetailComponent} from './project/components/group-detail/group-detail.component';
import {SnapshotDetailComponent} from './project/components/snapshot-detail/snapshot-detail.component';
import {SamplegroupListComponent} from './project/components/samplegroup-list/samplegroup-list.component';
import {BsDatepickerModule} from 'ngx-bootstrap/datepicker';
import {ModulesModule} from './modules/modules.module';
import {SharedModule} from './shared/shared.module';
import {AnalysisModule} from './analysis/analysis.module';
import {TimestampDetailResolve} from './project/containers/timestamp-detail/timestamp-detail-resolve';
import {PostprocessingResultDetailComponent} from './project/components/postprocessing-result-detail/postprocessing-result-detail.component';
import {NgxDatatableModule} from '@swimlane/ngx-datatable';
import {AnalysisListComponent} from './project/containers/analysis-list/analysis-list.component';
import {ViewBlocksModule} from './view-blocks/view-blocks.module';
import {PostprocessingResultsListComponent} from './project/containers/postprocessing-results-list/postprocessing-results-list.component';
import {AnalysisResultDetailComponent} from './project/containers/analysis-result-detail/analysis-result-detail.component';
import {JwtModule} from '@auth0/angular-jwt';
import {HttpClientModule, HttpHeaders} from '@angular/common/http';
import {HttpLink, HttpLinkModule} from 'apollo-angular-link-http';
import {environment} from '../environments/environment';
import {InMemoryCache} from 'apollo-cache-inmemory';
import {setContext} from 'apollo-link-context';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {ToastrModule, ToastrService} from 'ngx-toastr';
import {onError} from 'apollo-link-error';

@NgModule({
  declarations: [
    AppComponent,
    CreateProjectComponent,
    ProjectFormComponent,
    ProjectDashboardComponent,
    SampleGroupInputComponent,
    PageNotFoundComponent,
    PlantListComponent,
    SampleGroupComponent,
    ProjectDetailComponent,
    LoginComponent,
    EditProjectComponent,
    SampleGroupListComponent,
    ProjectDetailsComponent,
    TimestampDetailComponent,
    GroupDetailComponent,
    SnapshotDetailComponent,
    SamplegroupListComponent,
    PostprocessingResultDetailComponent,
    AnalysisListComponent,
    PostprocessingResultsListComponent,
    AnalysisResultDetailComponent
  ],
  imports     : [
    BrowserModule,
    ReactiveFormsModule,
    HttpClientModule,
    BrowserAnimationsModule,
    RouterModule.forRoot(appRoutes),
    JwtModule.forRoot({
      config: {
        tokenGetter       : () => {
          return localStorage.getItem('id_token')
        },
        whitelistedDomains: [/^null$/]//TODO proper instantiation via environment variables
      }
    }),
    HttpLinkModule,
    ApolloModule,
    ToastrModule.forRoot({
      timeOut          : 10000,
      positionClass    : 'toast-bottom-center',
      preventDuplicates: true,
    }),
    CollapseModule.forRoot(),
    AccordionModule.forRoot(),
    ModalModule.forRoot(),
    TooltipModule.forRoot(),
    BsDatepickerModule.forRoot(),
    SharedModule,
    ModulesModule,
    AnalysisModule,
    ViewBlocksModule,
    NgxDatatableModule
  ],
  providers   : [
    ExperimentsResolve,
    ExperimentResolve,
    TimestampDetailResolve,
    AuthService,
    AuthGuard,
    //AUTH_PROVIDERS
  ],
  exports     : [],
  bootstrap   : [AppComponent]
})
export class AppModule {
  constructor(apollo: Apollo, httpLink: HttpLink, router: Router, toastr: ToastrService) {
    const http = httpLink.create({uri: environment.baseUrl + environment.graphqlEndpoint});
    const cache = new InMemoryCache({
      dataIdFromObject: (result) => {
        return result['id'];
      },
      addTypename     : true
    });
    const middleware = setContext(() => ({
      headers: new HttpHeaders().set('Authorization', 'Bearer ' + localStorage.getItem('id_token') || null)
    }));
    const errorHandler = onError(({graphQLErrors, networkError}) => {
      if (graphQLErrors) {
        /*graphQLErrors.map(({message, locations, path}) =>
          console.log(
            `[GraphQL error]: Message: ${message}, Location: ${locations}, Path: ${path}`,
          ),
        );*/
      }

      if (networkError) {
        if (networkError['status'] == 401) {
          toastr.error('You have been logged out. Please log in again.');
          router.navigate(['/login'])
        }
      }
    });

    const link = middleware.concat(errorHandler).concat(http);
    apollo.create({
      link : link,
      cache: cache,
    });
  }
}
