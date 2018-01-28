import {Injectable} from '@angular/core';
import {ActivatedRouteSnapshot, Resolve, RouterStateSnapshot} from '@angular/router';
import {Apollo} from 'apollo-angular';
import {Observable} from 'rxjs/Observable';
import gql from 'graphql-tag';
import {map} from 'rxjs/operators';

const fetchTimestamp = gql`
  query fetchTimestamp($timestampId: ID!){
    timestamp(id: $timestampId){
      id
      createdAt
      completed
      analyses{
        edges{
          node{
            id
          }
        }
      }
    }
  }
`;

@Injectable()
export class TimestampDetailResolve implements Resolve<GQL.ITimestamp> {
  constructor(private apollo: Apollo) {
  }

  resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<GQL.ITimestamp> {
    return this.apollo.query<GQL.IGraphQLResponseRoot>({
      query      : fetchTimestamp,
      variables  : {timestampId: route.params['timestamp_id']},
      fetchPolicy: 'network-only'
    }).pipe(map((result) => {
      return result['data']['timestamp'];
    }));
  }

}
