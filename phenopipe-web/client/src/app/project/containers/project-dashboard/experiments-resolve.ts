import {ActivatedRouteSnapshot, Resolve, RouterStateSnapshot} from '@angular/router';
import {Observable} from 'rxjs';
import {Apollo} from 'apollo-angular';
import gql from 'graphql-tag/index';
import {ApolloQueryResult} from 'apollo-client';
import {Injectable} from '@angular/core';
import {map} from 'rxjs/operators';

const fetchExperiments = gql`
  query fetchExperiments{
    experiments{
      edges{
        node{
          id
          name
          scientist
          createdAt
          updatedAt
        }
      }
    }
  }
`;

@Injectable()
export class ExperimentsResolve implements Resolve<ApolloQueryResult<GQL.IExperiment[]>> {
  constructor(private apollo: Apollo) {
  }

  resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<ApolloQueryResult<GQL.IExperiment[]>> {
    return <Observable<ApolloQueryResult<GQL.IExperiment[]>>>Observable.from(
      this.apollo.query<GQL.IGraphQLResponseRoot>({
        fetchPolicy: 'network-only',
        query      : fetchExperiments,
      })).pipe(
      map(
        (result: ApolloQueryResult<GQL.IGraphQLResponseRoot>) => {
          let res: {} = {};
          res['data'] = result['data']['experiments'];
          res['loading'] = result['loading'];
          res['networkStatus'] = result['networkStatus'];
          return res;
        }
      ));
  }


}
