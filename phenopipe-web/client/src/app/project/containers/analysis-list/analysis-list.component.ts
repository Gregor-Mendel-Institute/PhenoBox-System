import {Component, Input, OnInit, ViewChild} from '@angular/core';
import gql from 'graphql-tag';
import {Apollo} from 'apollo-angular';
import {ApolloQueryResult} from 'apollo-client';
import {Observable} from 'rxjs/Observable';
import {AccordionPanelComponent} from 'ngx-bootstrap';
import {DownloadService} from '../../../shared/download-results-service/download-results.service';
import {TemplateUtilsService} from '../../../shared/template-utils.service';
import {Router} from '@angular/router';
import {ToastrService} from 'ngx-toastr';


const fetchAnalyses = gql`
  query fetchAnalyses($timestampID:ID!){
    analyses(forTimestamp:$timestampID){
      edges{
        node{
          iapId
          id
          pipeline{
            id
            name
          }
          startedAt
          finishedAt
          snapshots{
            edges{
              node{
                id
              }
            }
          }
          postprocessings{
            edges{
              node{
                id
              }
            }
          }
        }
      }
    }
  }
`;
//TODO remove because unused
const fetchSampleGroups = gql`
  query fetchSampleGroups($analysisID:ID!){
    sampleGroups(forAnalysis: $analysisID) {
      edges{
        node{
          id
          name
          description
          plants {
            edges {
              node {
                id
                index
                name
                fullName
                snapshots {
                  edges {
                    node {
                      id

                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
`;

@Component({
  selector   : 'app-analysis-list',
  templateUrl: './analysis-list.component.html',
  styleUrls  : ['./analysis-list.component.css']
})
export class AnalysisListComponent implements OnInit {
  @Input()
  timestampId: string;
  @Input()
  experimentId: string;
  @ViewChild('agroup') accordion: any;

  analyse$: Observable<GQL.IAnalysisEdge[]>;
  analyses: GQL.IAnalysisEdge[];
  fetchedGroups: { [key: string]: Observable<GQL.ISampleGroupEdge[]> } = {};

  constructor(private apollo: Apollo, private router: Router, private templateUtils: TemplateUtilsService,
              private downloadService: DownloadService, private toastr: ToastrService) {
  }

  private fetchAnalyses(timestampId: string): Observable<GQL.IAnalysisEdge[]> {
    return this.apollo.watchQuery({
        query    : fetchAnalyses,
        variables: {timestampID: timestampId},
      }
    ).valueChanges.map((result: ApolloQueryResult<GQL.IGraphQLResponseRoot>) => {
      return result.data['analyses'].edges

    });
  }

  private fetchSampleGroups(analysisId: string): Observable<GQL.ISampleGroupEdge[]> {
    return this.apollo.watchQuery({
        query    : fetchSampleGroups,
        variables: {analysisID: analysisId},
      }
    ).valueChanges.map((result: ApolloQueryResult<GQL.IGraphQLResponseRoot>) => {
      return result.data['sampleGroups'].edges
    });
  }

  ngOnInit() {
    this.analyse$ = this.fetchAnalyses(this.timestampId);
    this.analyse$.subscribe((val) => {
      this.analyses = val;
    }, (err) => {
      if(err.graphQLErrors) {
        this.toastr.error(err.graphQLErrors[0].message);
      }else{
        this.toastr.error(err.message);
      }
    });
  }

  private onActivate(event) {
    if (event.type == 'click') {
      this.router.navigate(["results", this.timestampId, event.row.node.id])
    }
  }

  accordionGroupClicked(accordion: AccordionPanelComponent, analysis: GQL.IAnalysisEdge) {
    if (accordion.isOpen && !this.fetchedGroups[analysis.node.id]) {
      this.fetchedGroups[analysis.node.id] = this.fetchSampleGroups(analysis.node.id);
    }
  }

  downloadResults(analysis: GQL.IAnalysisEdge, withPictures: boolean) {
    this.downloadService.downloadResults(analysis.node.id, withPictures).subscribe(
      (res) => {
        console.log(res);
      });
  }
}
