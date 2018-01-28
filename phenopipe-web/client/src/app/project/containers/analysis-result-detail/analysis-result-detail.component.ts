import {Component, OnInit} from '@angular/core';
import gql from 'graphql-tag';
import {ActivatedRoute} from '@angular/router';
import {Observable} from 'rxjs/Observable';
import {Apollo} from 'apollo-angular';
import {ApolloQueryResult} from 'apollo-client';
import {TemplateUtilsService} from '../../../shared/template-utils.service';
import {DownloadService} from '../../../shared/download-results-service/download-results.service';

const fetchAnalysis = gql`
  query fetchAnalysis($id:ID!){
    analysis(id:$id){
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
        experiment{
          id
          name
        }
      }
      sampleGroups {
        edges {
          node {
            name
            description
            treatment
            species
            genotype
            growthConditions
            variety
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
                        images {
                          edges {
                            node {
                              id
                              angle
                              type
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
`;

@Component({
  selector   : 'app-analysis-result-detail',
  templateUrl: './analysis-result-detail.component.html',
  styleUrls  : ['./analysis-result-detail.component.css']
})
export class AnalysisResultDetailComponent implements OnInit {

  analysis: GQL.IAnalysis;

  constructor(private downloadService: DownloadService,private apollo: Apollo, private activeRoute: ActivatedRoute, private templateUtils: TemplateUtilsService) {

  }

  ngOnInit() {
    this.loadAnalysis(this.activeRoute.snapshot.params.analysis_id).subscribe((analysis) => {
      this.analysis = analysis;
      console.log(analysis);
    })
  }

  private loadAnalysis(analysisId: string): Observable<GQL.IAnalysis> {
    return this.apollo.watchQuery({
        query    : fetchAnalysis,
        variables: {id: analysisId}
      }
    ).valueChanges.map((result: ApolloQueryResult<GQL.IGraphQLResponseRoot>) => {
      return result.data['analysis']
    });
  }

  downloadResults(analysis: GQL.IAnalysis, withPictures: boolean) {
    this.downloadService.downloadResults(analysis.id, withPictures).subscribe(
      (res) => {
        console.log(res);
      });

  }
}
