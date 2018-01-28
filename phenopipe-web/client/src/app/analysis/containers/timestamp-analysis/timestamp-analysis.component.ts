import {Component, OnInit, ViewChild} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import gql from 'graphql-tag';
import {Apollo, QueryRef} from 'apollo-angular';
import {map, startWith, withLatestFrom} from 'rxjs/operators';
import {Observable} from 'rxjs/Observable';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {ConditionalValidator} from '../../../shared/conditional-validator';
import {TemplateUtilsService} from '../../../shared/template-utils.service';
import {ApolloQueryResult} from 'apollo-client';
import {ProcessingService} from '../../services/processingService/processing.service';
import {ToastrService} from 'ngx-toastr';

const fetchExperimentInfo = gql`
  query fetchExperimentInfo($id:ID!){
    experiment(id:$id){
      id
      name
    }
  }`;

const fetchTimestampInfo = gql`
  query fetchTimestampInfo($id:ID!){
    timestamp(id: $id){
      id
      createdAt
      analyses{
        edges{
          node{
            id
            pipeline{
              id
              name
            }
            pipelineId
            startedAt
            finishedAt
          }
        }
      }
    }
  }`;
const fetchPostprocessingStacks = gql`
  query fetchPostprocessingStacks($analysis_id: ID){
    postprocessingStacks(unusedForAnalysis: $analysis_id){
      edges{
        node{
          id
          name
          description
          scripts{
            edges{
              node{
                id
                name
                description
              }
            }
          }
        }
      }
    }
  }`;

const fetchIapPipelines = gql`
  query fetchIapPipelines($timestamp_id:ID!){
    pipelines(unusedForTimestamp: $timestamp_id){
      edges {
        node {
          id
          name
          description
        }
      }
    }
  }`;

@Component({
  selector   : 'app-timestamp-analysis',
  templateUrl: './timestamp-analysis.component.html',
  styleUrls  : ['./timestamp-analysis.component.css']
})
export class TimestampAnalysisComponent implements OnInit {

  @ViewChild('stackSelector') stackSelector;

  private experimentId;
  private timestampId;
  private experimentInfo: Observable<GQL.IExperiment>;
  private timestampInfo: GQL.ITimestamp;
  private timestampInfo$: Observable<GQL.ITimestamp>;
  private stacksQuery: QueryRef<GQL.IGraphQLResponseRoot>;
  private postprocessingStack$: Observable<GQL.IPostprocessingStackEdge[]>;
  private currentStack: GQL.IPostprocessingStack;
  private currentPipeline: GQL.IPipelineEdge;
  private currentAnalysis: GQL.IAnalysis;
  private pipelineQuery: QueryRef<GQL.IGraphQLResponseRoot>;
  private pipeline$: Observable<GQL.IPipelineEdge[]>;
  pipelines: GQL.IPipelineEdge[];
  stacks: GQL.IPostprocessingStackEdge[];
  private analysis: FormGroup;

  constructor(private route: ActivatedRoute, private router: Router, private apollo: Apollo, private processingService: ProcessingService,
              private fb: FormBuilder, private toastr: ToastrService, private templateUtils: TemplateUtilsService) {
    route.params.subscribe((params) => {
      this.experimentId = decodeURIComponent(params.experiment_id);
      this.timestampId = decodeURIComponent(params.timestamp_id);
    });
  }

  private handleFetchError(err) {
    if (err.networkError && err.networkError.status == 401) {
      this.toastr.error('You have been logged out. Please log in again.');
      this.router.navigate(['/login']);
    } else if (err.graphQLErrors && err.graphQLErrors.length > 0) {
      this.toastr.error(err.graphQLErrors[0].message);
    } else {
      this.toastr.error(err.message);
    }
  }

  ngOnInit() {
    this.experimentInfo = this.loadExperimentInfo();
    this.timestampInfo$ = this.loadTimestampInfo();
    this.timestampInfo$.subscribe((results) => {
      this.timestampInfo = results;
    }, this.handleFetchError.bind(this));
    {
      let {query, results} = this.loadPipelines();
      this.pipelineQuery = query;
      this.pipeline$ = results;
      this.pipeline$.subscribe((results) => {
        this.pipelines = results;
      }, this.handleFetchError.bind(this));
    }
    this.analysis = this.setUpForm();
    {
      let {query, results} = this.loadPostprocessingStacks();
      this.postprocessingStack$ = results;
      this.stacksQuery = query;
      this.postprocessingStack$.subscribe((results) => {
        this.stacks = results;
      }, this.handleFetchError.bind(this));
      this.setUpRefetching(query);
    }
  }

  private setUpForm(): FormGroup {
    let validationConditionExisting = (group: FormGroup) => group.get('useExisting')
      .valueChanges.pipe(
        startWith(false)
      );
    let validationConditionNew = (group: FormGroup) => group.get('useExisting').valueChanges
      .pipe(
        map(v => !v),
        startWith(true)
      );
    let form = this.fb.group({
      useExisting    : [false],
      existing       : this.fb.group({
        id: [
          '', ConditionalValidator.create(Validators.required, validationConditionExisting)
        ],
      }),
      pipeline       : this.fb.group({
          id: [
            '', ConditionalValidator.create(Validators.required, validationConditionNew)
          ]
        }
      ),
      postprocessNote: ['']
    });

    //TODO use form binding instead of array find
    form.get('existing.id').valueChanges.pipe(
      withLatestFrom(this.timestampInfo$, (analysisId, timestamp) => ({analysisId, timestamp})),
      map(({analysisId, timestamp}) => {
        if (timestamp.analyses.edges) {
          let analysis = timestamp.analyses.edges.find((analysis) => analysis.node.id == analysisId);
          if (analysis) {
            return analysis.node
          } else {
            return {};
          }
        } else {
          return {};
        }
      })
    ).subscribe((analysis: GQL.IAnalysis) => {
      this.currentAnalysis = analysis;
    }, this.handleFetchError.bind(this));

    form.get('pipeline').valueChanges.pipe(
      withLatestFrom(this.pipeline$,
        (selection, pipelines) => ({selection, pipelines})),
      map(({selection, pipelines}) => {
        if (pipelines) {
          return pipelines.find((pipeline) => pipeline.node.id == selection.id);
        } else {
          return {};
        }
      })
    ).subscribe((pipeline: GQL.IPipelineEdge) => {
      this.currentPipeline = pipeline;
    }, this.handleFetchError.bind(this));
    return form;
  }

  private setUpRefetching(stacksQuery: QueryRef<GQL.IGraphQLResponseRoot>) {
    this.analysis.get('useExisting').valueChanges.subscribe((useExisting) => {
      if (!useExisting) {
        stacksQuery.refetch({analysis_id: null}).then((res) => {
        }, this.handleFetchError.bind(this));
      }
    });
    this.analysis.get('existing.id').valueChanges.subscribe((analysisId) => {
      if (analysisId !== '' && this.analysis.get('useExisting')) {
        stacksQuery.refetch({analysis_id: analysisId}).then((res) => {
          console.log(res);
        }, this.handleFetchError.bind(this));
      }
    });
  }

  private loadExperimentInfo(): Observable<GQL.IExperiment> {
    return this.apollo.query<GQL.IGraphQLResponseRoot>({
      query    : fetchExperimentInfo,
      variables: {id: this.experimentId},
    }).pipe(
      map((resp: ApolloQueryResult<GQL.IGraphQLResponseRoot>) => {
          return resp.data['experiment'];
        }
      ));
  }

  private loadTimestampInfo(): Observable<GQL.ITimestamp> {
    return this.apollo.watchQuery<GQL.IGraphQLResponseRoot>({
      query    : fetchTimestampInfo,
      variables: {id: this.timestampId},
    }).valueChanges.pipe(
      map((resp: ApolloQueryResult<GQL.IGraphQLResponseRoot>) => {
          return resp.data['timestamp'];
        }
      ));
  }

  private loadPipelines(): { query: QueryRef<GQL.IGraphQLResponseRoot>; results: Observable<GQL.IPipelineEdge[]> } {
    let query = this.apollo.watchQuery<GQL.IGraphQLResponseRoot>({
      query    : fetchIapPipelines,
      variables: {timestamp_id: this.timestampId}
    });
    let results = query.valueChanges.pipe(
      map((resp: ApolloQueryResult<GQL.IGraphQLResponseRoot>) => {
          return resp.data['pipelines'].edges;
        }
      )
    );
    return {
      query  : query,
      results: results
    };
  }

  private loadPostprocessingStacks(): { query: QueryRef<GQL.IGraphQLResponseRoot>; results: Observable<GQL.IPostprocessingStackEdge[]> } {
    let postprocessingStacksQuery: QueryRef<GQL.IGraphQLResponseRoot> = this.apollo.watchQuery<GQL.IGraphQLResponseRoot>(
      {
        query: fetchPostprocessingStacks,
      });

    let results = postprocessingStacksQuery.valueChanges.pipe(
      map((resp: ApolloQueryResult<GQL.IGraphQLResponseRoot>) => {
          if (resp.data['postprocessingStacks']) {
            return resp.data['postprocessingStacks'].edges;
          } else {
            return [];
          }
        }
      ));
    return {
      query  : postprocessingStacksQuery,
      results: results
    };
  }

  stackClicked(stack: GQL.IPostprocessingStack) {
    this.currentStack = stack;
  }


  private onSubmit() {
    console.log('submit');
    let stackIds: string[] = [];

    this.stackSelector.selectedStacks.forEach((stack) => stackIds.push(stack.node.id));

    if (this.analysis.get('useExisting').value) {
      this.processingService.invokePostprocess(
        this.analysis.get('existing.id').value,
        stackIds,
        this.analysis.get('postprocessNote').value
      ).subscribe((res) => {
        console.log(res);
        this.stacksQuery.refetch({analysis_id: this.analysis.get('existing.id').value});
        this.toastr.success('The actions have successfully been submitted');
      }, (err) => {
        console.log(err);
        this.toastr.error('The action was not successfull.' + err.error.msg);
      });
    } else {
      this.processingService.invokeAnalysis(
        this.timestampId,
        this.analysis.get('pipeline.id').value,
        stackIds,
        this.analysis.get('postprocessNote').value
      ).subscribe((res) => {
        console.log(res);
        this.analysis.get('pipeline.id').reset('');
        this.analysis.get('postprocessNote').reset('');
        this.pipelineQuery.refetch({variables: {timestamp_id: this.timestampId}});
        this.toastr.success('The actions have successfully been submitted');
      }, (err) => {
        this.toastr.error('The action was not successfull.' + err.error.msg);
      });
    }
  }

}
