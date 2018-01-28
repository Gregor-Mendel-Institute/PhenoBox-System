import {Component, OnInit, ViewChild} from '@angular/core';
import gql from 'graphql-tag';
import {Observable} from 'rxjs/Observable';
import {Apollo, QueryRef} from 'apollo-angular';
import {ApolloQueryResult} from 'apollo-client';
import {ProcessingService} from '../../services/processingService/processing.service';
import {ActivatedRoute} from '@angular/router';
import {TemplateUtilsService} from '../../../shared/template-utils.service';
import {ToastrService} from 'ngx-toastr';

const fetchPostprocessingStacks = gql`
  query fetchPostprocessingStacks($analysisId: ID){
    postprocessingStacks(unusedForAnalysis: $analysisId){
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

const fetchAnalysis = gql`
  query fetchAnalysis($analysisId:ID!){
    analysis(id:$analysisId){
      iapId
      id
      pipeline{
        id
        name
      }
      startedAt
      finishedAt
      timestamp{
        id
        createdAt
        experiment
        {
          id
          name
        }
      }
      snapshots{
        edges{
          node{
            id
          }
        }
      }
    }
  }
`;

@Component({
  selector   : 'app-analysis-postprocessing',
  templateUrl: './analysis-postprocessing.component.html',
  styleUrls  : ['./analysis-postprocessing.component.css']
})
export class AnalysisPostprocessingComponent implements OnInit {


  @ViewChild('stackSelector') stackSelector;
  @ViewChild('postprocessingNote') postprocessingNote;

  private experimentId: string;
  private analysisId: string;
  private analysis: GQL.IAnalysis;
  private stacksQuery: QueryRef<GQL.IGraphQLResponseRoot>;
  postprocessingStacks: GQL.IPostprocessingStackEdge[] = [];
  currentStack: GQL.IPostprocessingStack;
  alert: { type: string; msg: string; timeout: number; } = null;

  constructor(private processingService: ProcessingService, private templateUtils: TemplateUtilsService,
              private apollo: Apollo, private route: ActivatedRoute, private toastr: ToastrService,) {
    console.log(route.snapshot.params);
    route.params.subscribe((params) => {
      this.experimentId = decodeURIComponent(params.experiment_id);
      this.analysisId = decodeURIComponent(params.analysis_id);
      console.log(this.analysisId);
      this.loadAnalysis().subscribe((analysis) => {
        this.analysis = analysis;
        console.log(analysis);
      });
    });
  }


  ngOnInit() {
    let {query, results} = this.loadPostprocessingStacks();
    results.subscribe((stacks) => {
      this.postprocessingStacks = stacks;
    });

  }

  private loadAnalysis() {
    return this.apollo.watchQuery<GQL.IGraphQLResponseRoot>(
      {
        query    : fetchAnalysis,
        variables: {analysisId: this.analysisId}
      }).valueChanges.map((resp: ApolloQueryResult<GQL.IGraphQLResponseRoot>) => {
        return resp.data['analysis'];
      }
    );
  }

  private loadPostprocessingStacks(): { query: QueryRef<GQL.IGraphQLResponseRoot>; results: Observable<GQL.IPostprocessingStackEdge[]> } {
    let query = this.apollo.watchQuery<GQL.IGraphQLResponseRoot>(
      {
        query    : fetchPostprocessingStacks,
        variables: {analysisId: this.analysisId}
      });
    let results = query.valueChanges.map((resp: ApolloQueryResult<GQL.IGraphQLResponseRoot>) => {
        return resp.data['postprocessingStacks'].edges;
      }
    );
    return {
      query  : query,
      results: results
    };
  }

  stackClicked(stack: GQL.IPostprocessingStack) {
    this.currentStack = stack;
  }

  submit() {
    let stackIds: string[] = [];
    this.stackSelector.selectedStacks.forEach((stack) => stackIds.push(stack.node.id));
    console.log(this.postprocessingNote);
    this.processingService.invokePostprocess(this.analysisId, stackIds, this.postprocessingNote.nativeElement.value)
      .subscribe((res) => {
        this.toastr.success('The actions have successfully been submitted');
      }, (err) => {
        this.toastr.error('The action was not successfull.' + err.error.msg);
      });
  }

}
