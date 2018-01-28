import {Component, OnInit} from '@angular/core';
import {Observable} from 'rxjs/Observable';
import gql from 'graphql-tag';
import {Apollo} from 'apollo-angular';

const fetchPostprocessingStatuses = gql`
  query fetchPostprocessingStatuses{
    postprocessingTaskStatuses {
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
  selector   : 'app-postprocessing-dashboard',
  templateUrl: './postprocessing-dashboard.component.html',
  styleUrls  : ['./postprocessing-dashboard.component.css']
})
export class PostprocessingDashboardComponent implements OnInit {

  postprocessingStatu$: Observable<GQL.ITaskStatusConnection>;

  constructor(private apollo: Apollo) {
  }

  ngOnInit() {
    this.postprocessingStatu$ = this.apollo.watchQuery<GQL.IGraphQLResponseRoot>({
      query: fetchPostprocessingStatuses,
    }).valueChanges.map((resp) => {
        return resp['data']['postprocessingTaskStatuses'];
      }
    );
  }

}
