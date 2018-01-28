import {Component, OnInit} from '@angular/core';
import gql from 'graphql-tag';
import {Apollo} from 'apollo-angular';
import {Observable} from 'rxjs/Observable';

const fetchAnalysisStatuses = gql`
  query fetchAnalysisStatuses{
    analysisTaskStatuses {
      edges {
        node {
          id
          name
          description
          currentStatus
          currentMessage
          jobs {
            edges {
              node {
                name
                id
                description
                status
                enqueuedAt
                startedAt
                finishedAt
              }
            }
          }
        }
      }
    }
  }`;


@Component({
  selector   : 'app-analysis-dashboard',
  templateUrl: './analysis-dashboard.component.html',
  styleUrls  : ['./analysis-dashboard.component.css']
})
export class AnalysisDashboardComponent implements OnInit {

  analysisStatu$: Observable<GQL.ITaskStatusConnection>;

  constructor(private apollo: Apollo) {
  }

  ngOnInit() {
    this.analysisStatu$ = this.apollo.watchQuery<GQL.IGraphQLResponseRoot>({
      query: fetchAnalysisStatuses,
    }).valueChanges.map((resp) => {
        return resp['data']['analysisTaskStatuses'];
      }
    );

  }


}
