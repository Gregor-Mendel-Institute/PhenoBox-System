import {ActivatedRouteSnapshot, Resolve, RouterStateSnapshot} from '@angular/router';
import gql from 'graphql-tag/index';
import {ApolloQueryResult} from 'apollo-client';
import {Observable} from 'rxjs';
import {Injectable} from '@angular/core';
import {Apollo} from 'apollo-angular';

//TODO remove as much from timestamp as possible (all except id?)
const fetchExperiment = gql`
  query fetchExperiment($id:ID!){
    experiment(id:$id){
      id
      name
      description
      scientist
      groupName
      startDate
      startOfExperimentation
      createdAt
      updatedAt
      timestamps{
        edges{
          node{
            id
            createdAt
            completed
          }
        }
      }
      sampleGroups{
        edges{
          node{
            name
            description
            isControl
            treatment
            species
            genotype
            variety
            growthConditions
            id
            plants{
              edges{
                node{
                  id
                  index
                  name
                  fullName
                }
              }
            }
          }
        }
      }
    }
  }
`;

@Injectable()
export class ExperimentResolve implements Resolve<ApolloQueryResult<GQL.IExperiment>> {
  constructor(private apollo: Apollo) {
  }

  resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<ApolloQueryResult<GQL.IExperiment>>
    | Promise<ApolloQueryResult<GQL.IExperiment>>
    | ApolloQueryResult<GQL.IExperiment> {

    return <Observable<ApolloQueryResult<GQL.IExperiment>>>Observable.from(this.apollo.query<GQL.IGraphQLResponseRoot>({
      query      : fetchExperiment,
      variables  : {id: route.params['id']},
      fetchPolicy: 'network-only'
    })).map((result: ApolloQueryResult<GQL.IGraphQLResponseRoot>) => {
      let res: {} = {};
      res['data'] = result.data['experiment'];
      res['loading'] = result.loading;
      res['networkStatus'] = result.networkStatus;
      return res;
    });
  }

}
