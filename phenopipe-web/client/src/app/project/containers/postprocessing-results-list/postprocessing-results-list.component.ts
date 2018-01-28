import {Component, Input, OnInit} from '@angular/core';
import gql from 'graphql-tag';
import {Observable} from 'rxjs/Observable';
import {Apollo} from 'apollo-angular';
import {ApolloQueryResult} from 'apollo-client';
import {AccordionPanelComponent} from 'ngx-bootstrap';
import {TemplateUtilsService} from '../../../shared/template-utils.service';
import {ActivatedRoute, Router} from '@angular/router';

//TODO load sampleGroups lazily
const fetchPostprocessings = gql`
  query fetchPostprocessings($analysisID:ID!){
    postprocessings(forAnalysis:$analysisID){
      edges{
        node{
          id
          startedAt
          finishedAt
          note
          sampleGroups {
            edges {
              node {
                name
                plants {
                  edges {
                    node {
                      id
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
    }
  }
`;

const fetchSampleGroup = gql`
  query fetchSampleGroup($id:ID!){
    sampleGroup(id: $id) {
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
  selector   : 'app-postprocessing-results-list',
  templateUrl: './postprocessing-results-list.component.html',
  styleUrls  : ['./postprocessing-results-list.component.css']
})
export class PostprocessingResultsListComponent implements OnInit {
  @Input()
  private analysisId: string;

  postprocessing$: Observable<GQL.IPostprocessEdge[]>;
  fetchedGroups: { [key: string]: GQL.ISampleGroup[] } = {};

  constructor(private apollo: Apollo, private router: Router, private activeRoute: ActivatedRoute, private templateUtils: TemplateUtilsService) {
  }

  ngOnInit() {
    this.postprocessing$ = this.loadPostprocessings();
    this.postprocessing$.subscribe((stack) => {
      console.log(stack);
    })
  }

  private calculateNumberOfPlants(postprocess: GQL.IPostprocessEdge) {
    let count = 0;
    postprocess.node.sampleGroups.edges.forEach((group) => count += group.node.plants.edges.length);
    return count;
  }

  private loadPostprocessings(): Observable<GQL.IPostprocessEdge[]> {
    return this.apollo.watchQuery({
        query    : fetchPostprocessings,
        variables: {analysisID: this.analysisId}
      }
    ).valueChanges.map((result: ApolloQueryResult<GQL.IGraphQLResponseRoot>) => {
      return result.data['postprocessings'].edges
    });
  }

  private fetchSampleGroup(groupId: string): Observable<GQL.ISampleGroup> {
    return this.apollo.watchQuery({
        query    : fetchSampleGroup,
        variables: {id: groupId},
      }
    ).valueChanges.map((result: ApolloQueryResult<GQL.IGraphQLResponseRoot>) => {
      return result.data['sampleGroup']
    });
  }

  private onActivate(event) {
    if (event.type == 'click') {
      this.router.navigate([event.row.node.id], {relativeTo: this.activeRoute})
    }

  }

  accordionGroupClicked(accordion: AccordionPanelComponent, postprocess: GQL.IPostprocessEdge) {
    if (accordion.isOpen && !this.fetchedGroups[postprocess.node.id]) {
      let groups: GQL.ISampleGroup[] = [];//TODO Use an observable?
      postprocess.node.sampleGroups.edges.forEach((group) => {
        this.fetchSampleGroup(group.node.id).subscribe((group) => groups.push(group));
      });
      this.fetchedGroups[postprocess.node.id] = groups;
    }
  }
}
