import {Component, OnInit} from '@angular/core';
import {Observable} from 'rxjs/Observable';
import gql from 'graphql-tag';
import {Apollo} from 'apollo-angular';

const fetchPostprocessingTasks = gql`
  query fetchPostprocessingTasks{
    postprocessingTasks {
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

  postprocessingStatu$: Observable<GQL.ITaskConnection>;

  constructor(private apollo: Apollo) {
  }

  ngOnInit() {
    this.postprocessingStatu$ = this.apollo.watchQuery<GQL.IGraphQLResponseRoot>({
      query: fetchPostprocessingTasks,
    }).valueChanges.map((resp) => {
      return resp['data']['postprocessingTasks'];
      }
    );
  }

}
