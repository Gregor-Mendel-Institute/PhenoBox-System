import {Component, OnInit} from '@angular/core';
import gql from 'graphql-tag';
import {Apollo} from 'apollo-angular';
import {Observable} from 'rxjs/Observable';

const fetchAnalysisTasks = gql`
  query fetchAnalysisTasks{
    analysisTasks {
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

  analysisTask$: Observable<GQL.ITaskConnection>;

  constructor(private apollo: Apollo) {
  }

  ngOnInit() {
    this.analysisTask$ = this.apollo.watchQuery<GQL.IGraphQLResponseRoot>({
      query: fetchAnalysisTasks,
    }).valueChanges.map((resp) => {
      return resp['data']['analysisTasks'];
      }
    );

  }


}
