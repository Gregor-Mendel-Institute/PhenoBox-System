import {Component, Input, OnInit, ViewChild} from '@angular/core';
import gql from 'graphql-tag';
import {Apollo, QueryRef} from 'apollo-angular';
import {ApolloQueryResult} from 'apollo-client';
import 'rxjs/add/observable/fromPromise';
import {ActivatedRoute} from '@angular/router';
import {Observable} from 'rxjs/Observable';
import {ModalDirective} from 'ngx-bootstrap';
import {ChangeSnapshotExclusionEvent, DeleteSnapshotEvent} from '../../components/group-detail/group-detail.component';
import {findIndex} from 'lodash';
import {DownloadService} from '../../../shared/download-results-service/download-results.service';
import {map} from 'rxjs/operators';
import {ToastrService} from 'ngx-toastr';

const fetchSampleGroups = gql`
  query fetchSampleGroups($timestampID:ID!){
    sampleGroups(forTimestamp:$timestampID){
      edges{
        node{
          name
          description
          treatment
          species
          genotype
          growthConditions
          variety
          isControl
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
                      excluded
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
`;

const finalizeTimestamp = gql`
  mutation completeTimestamp($timestampId: ID!){
    completeTimestamp(timestampId: $timestampId){
      id
    }
  }
`;
const changeSnapshotExclusion = gql`
  mutation changeSnapshotExclusion($snapshotId: ID!, $exclude:Boolean!){
    changeSnapshotExclusion(snapshotId: $snapshotId, exclude:$exclude){
      id
      excluded
    }
  }
`;
const deleteSnapshot = gql`
  mutation deleteSnapshot($snapshotId: ID!){
    deleteSnapshot(id: $snapshotId){
      id
    }
  }
`;


@Component({
  selector   : 'app-timestamp-detail',
  templateUrl: './timestamp-detail.component.html',
  styleUrls  : ['./timestamp-detail.component.css']
})
export class TimestampDetailComponent implements OnInit {
  @Input()
  experimentId: string;
  @Input()
  timestamp: GQL.ITimestamp;

  @ViewChild('finalizeModal') private finalizeModal: ModalDirective;

  private sampleGroupsQuery: QueryRef<GQL.IGraphQLResponseRoot> = null;
  private sampleGroup$: Observable<GQL.ISampleGroupEdge[]>;
  private totalImagedPlants: number;

  constructor(private route: ActivatedRoute, private apollo: Apollo, private downloadService: DownloadService, private toastr: ToastrService) {
    if (!this.experimentId || !this.timestamp) {
      this.experimentId = route.parent.snapshot.params.id;
    }
  }

  private fetchSampleGroups(timestampId: string) {
    if (!this.sampleGroupsQuery) {
      this.sampleGroupsQuery = this.apollo.watchQuery({
          query    : fetchSampleGroups,
          variables: {timestampID: timestampId},
        }
      );
      return this.sampleGroupsQuery.valueChanges.pipe(map((result: ApolloQueryResult<GQL.IGraphQLResponseRoot>) => {
        return result.data['sampleGroups'].edges
      }));
    }
    else {
      return Observable.fromPromise(this.sampleGroupsQuery.refetch({timestampID: timestampId}))
        .pipe(
          map((result: ApolloQueryResult<GQL.IGraphQLResponseRoot>) => {
            return result.data['sampleGroups'].edges;
          })
        );
    }
  }

  ngOnInit() {
    this.route.data.subscribe((data) => {
      this.timestamp = data['timestamp'];
      console.log(this.timestamp);
      this.sampleGroup$ = this.fetchSampleGroups(this.timestamp.id);

      this.sampleGroup$.subscribe((groups) => {
        let totalImaged = 0;
        groups.forEach((group) => {
          totalImaged += group.node.plants.edges.length;
        });
        this.totalImagedPlants = totalImaged;
      })
    });
  }

  private deleteSnapshot(event: DeleteSnapshotEvent) {
    console.log('delete Snapshot: ', event.snapshotId);
    this.apollo.mutate({
      mutation : deleteSnapshot,
      variables: {
        snapshotId: event.snapshotId
      },
      update   : (proxy, {data: {deleteSnapshot}}) => {
        //FIXME deleting empty sample groups doesn't work
        const data = proxy.readQuery(
          {
            query    : fetchSampleGroups,
            variables: {timestampID: this.timestamp.id}
          });

        let groupIndex = findIndex(data['sampleGroups'].edges,
          (group: GQL.ISampleGroupEdge) => group.node.id == event.groupId);
        let remainingPlants = data['sampleGroups'].edges[groupIndex].node.plants.edges.filter(
          (plant) => plant.node.id != event.plantId);
        data['sampleGroups'].edges[groupIndex].node.plants.edges = remainingPlants;
        proxy.writeQuery({query: fetchSampleGroups, data: data});
      }
    }).subscribe(({data}) => {
      this.totalImagedPlants--;
      //Remove snapshot from data to refresh component
      /*setTimeout(() => {
        this.sampleGroup$ = this.fetchSampleGroups(this.timestamp.id);
      });*/
    }, (err) => {
      this.toastr.error('Deleting the snapshot with ID ' + event.snapshotId + 'failed. Please reload the page');
    });
  }

  //TODO move to a shared service? Or down into the sampleGroup list?
  private changeSnapshotExclusion(event: ChangeSnapshotExclusionEvent) {
    this.apollo.mutate({
        mutation : changeSnapshotExclusion,
        variables: {
          snapshotId: event.snapshotId,
          exclude   : event.exclude
        },
        update   : (proxy, {data: {changeSnapshotExclusion}}) => {
          const data = proxy.readQuery(
            {
              query    : fetchSampleGroups,
              variables: {timestampID: this.timestamp.id}
            });

          let groupIndex = findIndex(data['sampleGroups'].edges,
            (group: GQL.ISampleGroupEdge) => group.node.id == event.groupId);
          let plantIndex = findIndex(data['sampleGroups'].edges[groupIndex].node.plants.edges,
            (plant: GQL.IPlantEdge) => plant.node.id == event.plantId);
          data['sampleGroups'].edges[groupIndex].node.plants.edges[plantIndex].node
            .snapshots.edges[0].node.excluded = event.exclude;
          proxy.writeQuery({query: fetchSampleGroups, data: data});
        }
      }
      ,).subscribe(({data}) => {
      /*setTimeout(() => {
        this.sampleGroup$ = this.fetchSampleGroups(this.timestamp.id);
      });*/
    }, (err) => {
      if (err.graphQLErrors.length > 0) {
        this.toastr.error(err.graphQLErrors[0].message)
      } else {
        this.toastr.error(err.message);
      }
    });
  }


  private confirmFinalize() {
    this.finalizeModal.hide();
    this.finalize();
  }

  private finalize() {
    console.log('finalize timestamp ', this.timestamp.id);
    this.apollo.mutate({
      mutation : finalizeTimestamp,
      variables: {
        timestampId: this.timestamp.id
      }
    }).subscribe(({data}) => {
      this.timestamp = Object.assign({}, this.timestamp, {completed: true});
    }, (err) => {
      //TODO use error message
      this.toastr.error('Finalizing the timestamp failed')
    });
  }

  downloadImages() {
    this.downloadService.downloadImages(this.timestamp.id).subscribe(
      (res) => {
        console.log(res);
      });

  }

}
