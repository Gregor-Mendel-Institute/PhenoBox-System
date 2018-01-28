import {Component, OnInit} from '@angular/core';
import gql from 'graphql-tag';
import {Apollo} from 'apollo-angular';
import {Observable} from 'rxjs/Observable';
import {ToastrService} from 'ngx-toastr';

const fetchPostprocessingStacks = gql`
  query fetchPostprocessingStacks{
    postprocessingStacks{
      edges{
        node{
          id
          name
          description
          scripts{
            edges{
              node{
                name
                description
              }
            }
          }
        }
      }
    }
  }`;

@Component({
  selector   : 'app-postprocessing-stacks',
  templateUrl: './postprocessing-stacks.component.html',
  styleUrls  : ['./postprocessing-stacks.component.css']
})
export class PostprocessingStacksComponent implements OnInit {

  postprocessingStack$: Observable<GQL.IPostprocessingStackConnection>;
  sortedPostprocessingStacks: GQL.IPostprocessingStackEdge[] = [];
  private error: { error: string; code: number; } = null;

  constructor(private apollo: Apollo) {
  }

  ngOnInit() {
    this.postprocessingStack$ = this.apollo.watchQuery<GQL.IGraphQLResponseRoot>({
      query: fetchPostprocessingStacks,
    }).valueChanges.map((resp) => {
        return resp['data']['postprocessingStacks'];
      }
    );
    this.postprocessingStack$.subscribe((stacks) => {
      console.log(stacks);
      let tmp :GQL.IPostprocessingStackEdge[]=[];
      stacks.edges.forEach((stack) => {
        tmp.push(Object.assign({}, stack));
      });
      tmp.sort((a, b) => {
        let a_n = a.node.name.toLowerCase();
        let b_n = b.node.name.toLowerCase();
        if (a_n < b_n) {
          return -1;
        }
        if (a_n > b_n) {
          return 1;
        }
        return 0;
      });
      this.sortedPostprocessingStacks =tmp;
      console.log(this.sortedPostprocessingStacks);
    }, (error) => {
      this.error = error.graphQLErrors[0];
    });

  }


}
