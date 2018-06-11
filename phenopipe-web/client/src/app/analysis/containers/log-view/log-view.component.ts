import {Component, ElementRef, OnInit} from '@angular/core';
import gql from 'graphql-tag';
import {ApolloQueryResult} from 'apollo-client';
import {Apollo, QueryRef} from 'apollo-angular';
import {ActivatedRoute} from '@angular/router';
import {TemplateUtilsService} from '../../../shared/template-utils.service';

const fetchJobLog = gql`
  query fetchJobLog($jobId:ID!, $newestFirst:Boolean, $cursor: String, $limit:Int){
    job(id: $jobId) {
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
  selector   : 'app-log-view',
  templateUrl: './log-view.component.html',
  styleUrls  : ['./log-view.component.css']
})
export class LogViewComponent implements OnInit {
  private jobIds: string[];
  private jobQueries: QueryRef<GQL.IGraphQLResponseRoot>[] = [];
  private jobs: GQL.IJob[] = [];
  private newestFirst: boolean = true;
  private cursors: string[] = [];
  private isLoading: boolean[] = [];
  private tabs: any[] = [];

  constructor(private activeRoute: ActivatedRoute, private apollo: Apollo, private el: ElementRef, private templateUtils: TemplateUtilsService) {
  }

  private loadJob(query: QueryRef<GQL.IGraphQLResponseRoot>) {
    return query.valueChanges.map((resp: ApolloQueryResult<GQL.IGraphQLResponseRoot>) => {
        return resp.data['job'];
      }
    );
  }

  loadMore(limit: number, index: number) {
    if (!this.isLoading[index] && this.cursors[index] != null) {//TODO use hasNextPage?
      console.log('Load more');
      this.isLoading[index] = true;
      this.jobQueries[index].fetchMore({
        query      : fetchJobLog, variables: {
          jobId      : this.jobIds[index],
          cursor     : this.jobs[index].log.pageInfo.endCursor,
          limit      : limit,
          newestFirst: this.newestFirst
        },
        updateQuery: (prev, {fetchMoreResult}) => {
          this.cursors[index] = fetchMoreResult['job'].log.pageInfo.endCursor;
          return Object.assign({}, prev,
            {
              job: Object.assign({}, ...prev['job'], {
                log: Object.assign({}, fetchMoreResult['job'].log,
                  {
                    edges: [
                      ...prev['job'].log.edges,
                      ...fetchMoreResult['job'].log.edges
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
    this.activeRoute.queryParams.subscribe((params) => {
      //If only a single id is passed the content of params['job_ids'] is no array
      if (params['job_ids'] instanceof Array) {
        this.jobIds = params['job_ids'];
      } else {
        this.jobIds[0] = params['job_ids'];
      }
      this.jobIds.forEach((jobId, i) => {
        this.cursors[i] = "";
        this.isLoading[i] = false;
        this.jobQueries[i] = this.apollo.watchQuery<GQL.IGraphQLResponseRoot>(
          {
            query    : fetchJobLog,
            variables: {
              jobId      : jobId,
              cursor     : this.cursors[i],
              limit      : 20,
              newestFirst: this.newestFirst
            }
          });
        this.loadJob(this.jobQueries[i]).subscribe((job) => {
          this.jobs[i] = job;
          if (this.tabs.length != this.jobIds.length) {
            this.tabs[i] = {'title': job.name, 'active': i === 0}
          }

          this.isLoading[i] = false;
        })
      });
    });
  }

  onTabSelected(event, index) {
    console.log(event);
  }
}










