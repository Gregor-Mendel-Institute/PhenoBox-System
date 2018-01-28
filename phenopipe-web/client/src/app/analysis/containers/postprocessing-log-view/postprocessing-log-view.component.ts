import {Component, OnInit} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import gql from 'graphql-tag';
import {Apollo, QueryRef} from 'apollo-angular';
import {ApolloQueryResult} from 'apollo-client';


const fetchPostprocessingTaskStatusLog = gql`
  query fetchPostprocessingTaskStatusLog($statusId:ID!,$newestFirst:Boolean, $cursor: String, $limit:Int){
    postprocessingTaskStatus(id: $statusId) {
      id
      name
      log(first:$limit, after:$cursor, newestFirst: $newestFirst){
        totalCount
        pageInfo {
          endCursor
        }
        edges{
          node{
            id
            timestamp
            message
            progress
          }
        }
      }
    }
  }`;

@Component({
  selector   : 'app-postprocessing-log-view',
  templateUrl: './postprocessing-log-view.component.html',
  styleUrls  : ['./postprocessing-log-view.component.css']
})
export class PostprocessingLogViewComponent implements OnInit {

  private statusId: string;
  private taskQuery: QueryRef<GQL.IGraphQLResponseRoot>;
  private taskStatus: GQL.ITaskStatus;
  private newestFirst: boolean = true;
  private cursor: string = "";
  private isLoading: boolean = false;

  constructor(private activeRoute: ActivatedRoute, private apollo: Apollo) {

  }

  loadMore(limit: number) {
    if (!this.isLoading && this.cursor != null) {
      this.isLoading = true;
      this.taskQuery.fetchMore({
        query      : fetchPostprocessingTaskStatusLog, variables: {
          statusId   : this.statusId,
          cursor     : this.cursor,
          limit      : limit,
          newestFirst: this.newestFirst
        },
        updateQuery: (prev, {fetchMoreResult}) => {
          this.cursor = fetchMoreResult['postprocessingTaskStatus'].log.pageInfo.endCursor;
          return Object.assign({}, prev,
            {
              analysisTaskStatus: Object.assign({}, ...prev['postprocessingTaskStatus'], {
                log: Object.assign({}, fetchMoreResult['postprocessingTaskStatus'].log,
                  {
                    edges: [
                      ...prev['postprocessingTaskStatus'].log.edges,
                      ...fetchMoreResult['postprocessingTaskStatus'].log.edges
                    ]
                  })
              })
            }
          );
        }
      });
    }
  }
  private loadTaskStatus(query: QueryRef<GQL.IGraphQLResponseRoot>) {
    return query.valueChanges.map((resp: ApolloQueryResult<GQL.IGraphQLResponseRoot>) => {
        return resp.data['postprocessingTaskStatus'];
      }
    );
  }

  ngOnInit() {
    this.activeRoute.params.subscribe((params) => {
      this.statusId = params['status_id'];
      this.taskQuery= this.apollo.watchQuery<GQL.IGraphQLResponseRoot>(
        {
          query    : fetchPostprocessingTaskStatusLog,
          variables: {
            statusId   : this.statusId,
            cursor     : this.cursor,
            limit      : 20,
            newestFirst: this.newestFirst}
        });
      this.loadTaskStatus(this.taskQuery).subscribe((val) => {
        this.taskStatus = val;
        this.isLoading = false;
      });
    });

  }

}
