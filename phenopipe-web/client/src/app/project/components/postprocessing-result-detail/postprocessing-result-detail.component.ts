import {Component, OnInit, ViewChild} from '@angular/core';
import gql from 'graphql-tag';
import {ApolloQueryResult} from 'apollo-client';
import {Apollo} from 'apollo-angular';
import {TemplateUtilsService} from '../../../shared/template-utils.service';
import {ActivatedRoute} from '@angular/router';

const fetchPostprocessings = gql`
  query fetchPostprocessing($id:ID!){
    postprocess(id:$id){
      id
      startedAt
      finishedAt
      note
      analysis{
        id
        pipeline{
          id
          name
        }
        timestamp{
          id
          createdAt
          experiment{
            id
            name
          }
        }
      }
      sampleGroups {
        edges {
          node {
            name
            description
            treatment
            genotype
            variety
            growthConditions
            species
            plants {
              edges {
                node {
                  fullName
                  index
                  id
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
      postprocessingStack{
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
`;

@Component({
  selector   : 'app-postprocessing-result-detail',
  templateUrl: './postprocessing-result-detail.component.html',
  styleUrls  : ['./postprocessing-result-detail.component.css']
})
export class PostprocessingResultDetailComponent implements OnInit {

  @ViewChild('postprocessesTable') table: any;

  postprocessId: string;
  postprocess: GQL.IPostprocess;
  private error: { error: string; code: number; } = null;

  constructor(private apollo: Apollo, private activeRoute: ActivatedRoute, private templateUtils: TemplateUtilsService) {
    this.postprocessId = activeRoute.snapshot.params.postprocess_id;
  }

  ngOnInit() {
    this.fetchPostprocess().subscribe((postprocess) => {
      this.postprocess = postprocess;
    }, (error) => {
      console.log(error);
      this.error = error.graphQLErrors[0];
    });
  }

  private fetchPostprocess() {
    return this.apollo.watchQuery({
        query    : fetchPostprocessings,
        variables: {id: this.postprocessId}
      }
    ).valueChanges.map((result: ApolloQueryResult<GQL.IGraphQLResponseRoot>) => {
      return result.data['postprocess']
    });
  }

  toggleExpandRow(row) {
    console.log('Toggled Expand Row!', row);
    this.table.rowDetail.toggleExpandRow(row);
  }

  onDetailToggle(event) {
    console.log('Detail Toggled', event);
  }
}
