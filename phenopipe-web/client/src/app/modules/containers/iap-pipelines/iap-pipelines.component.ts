import {Component, OnInit} from '@angular/core';
import gql from 'graphql-tag';
import {Apollo} from 'apollo-angular';
import {environment} from '../../../../environments/environment';
import {HttpClient} from '@angular/common/http';
import {ToastrService} from 'ngx-toastr';


const fetchIapPipelines = gql`
  query fetchIapPipelines{
    pipelines {
      edges {
        node {
          name
          description
        }
      }
    }
  }`;

@Component({
  selector   : 'app-iap-pipelines',
  templateUrl: './iap-pipelines.component.html',
  styleUrls  : ['./iap-pipelines.component.css']
})
export class IapPipelinesComponent implements OnInit {
  private pipelines: GQL.IPipelineEdge[];
  private error: { error: string; code: number; };

  constructor(private apollo: Apollo, private http: HttpClient) {
  }

  ngOnInit() {
    this.apollo.query<GQL.IGraphQLResponseRoot>({
      query: fetchIapPipelines,
    }).map((resp) => {
        return resp['data']['pipelines'];
      }
    ).subscribe((pipelines) => {
      this.pipelines = pipelines.edges
    }, (error) => {
      console.log(error);
      this.error = error.graphQLErrors[0];
    });
  }

  private delete(event, pipeline_name) {
    //todo delete pipeline
    console.log('submit');
    let payload = {
      pipeline_name: pipeline_name
    };
    console.log(payload);
    this.http.post(environment.deleteIapPipelineEndpoint, payload)
      .subscribe((res) => {
        console.log(res);
      });

  }

}
