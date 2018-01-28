import {Component, ElementRef, OnInit} from '@angular/core';
import gql from 'graphql-tag';
import {ApolloQueryResult} from 'apollo-client';
import {Apollo, QueryRef} from 'apollo-angular';
import {ActivatedRoute} from '@angular/router';
import {TemplateUtilsService} from '../../../shared/template-utils.service';

const fetchAnalysisTaskStatusLog = gql`
  query fetchAnalysisTaskStatusLog($statusId:ID!, $newestFirst:Boolean, $cursor: String, $limit:Int){
    analysisTaskStatus(id: $statusId) {
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
  selector   : 'app-analysis-log-view',
  templateUrl: './analysis-log-view.component.html',
  styleUrls  : ['./analysis-log-view.component.css']
})
export class AnalysisLogViewComponent implements OnInit {
  private statusId: string;
  private taskQuery: QueryRef<GQL.IGraphQLResponseRoot>;
  private taskStatus: GQL.ITaskStatus;
  private newestFirst: boolean = true;
  private cursor: string = "";
  private isLoading: boolean = false;

  constructor(private activeRoute: ActivatedRoute, private apollo: Apollo, private el: ElementRef, private templateUtils: TemplateUtilsService) {
  }

  private loadTaskStatus(query: QueryRef<GQL.IGraphQLResponseRoot>) {
    return query.valueChanges.map((resp: ApolloQueryResult<GQL.IGraphQLResponseRoot>) => {
        return resp.data['analysisTaskStatus'];
      }
    );
  }

  loadMore(limit: number) {
    if (!this.isLoading && this.cursor != null) {//TODO use hasNextPage?
      this.isLoading = true;
      this.taskQuery.fetchMore({
        query      : fetchAnalysisTaskStatusLog, variables: {
          statusId   : this.statusId,
          cursor     : this.cursor,
          limit      : limit,
          newestFirst: this.newestFirst
        },
        updateQuery: (prev, {fetchMoreResult}) => {
          this.cursor = fetchMoreResult['analysisTaskStatus'].log.pageInfo.endCursor;
          return Object.assign({}, prev,
            {
              analysisTaskStatus: Object.assign({}, ...prev['analysisTaskStatus'], {
                log: Object.assign({}, fetchMoreResult['analysisTaskStatus'].log,
                  {
                    edges: [
                      ...prev['analysisTaskStatus'].log.edges,
                      ...fetchMoreResult['analysisTaskStatus'].log.edges
                    ]
                  })
              })
            }
          );
        }
      });
    }
  }

  ngOnInit() {

    this.activeRoute.params.subscribe((params) => {
      this.statusId = params['status_id'];
      this.taskQuery = this.apollo.watchQuery<GQL.IGraphQLResponseRoot>(
        {
          query    : fetchAnalysisTaskStatusLog,
          variables: {
            statusId   : this.statusId,
            cursor     : this.cursor,
            limit      : 20,
            newestFirst: this.newestFirst
          }
        });
      this.loadTaskStatus(this.taskQuery).subscribe((val) => {
        this.taskStatus = val;
        this.isLoading = false;
      })
      ;
    });
  }

}
