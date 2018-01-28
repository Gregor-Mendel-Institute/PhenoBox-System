import {Component, OnInit, ViewChild} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {ModalDirective} from 'ngx-bootstrap';
import {environment} from '../../../../environments/environment';
import gql from 'graphql-tag/index';
import * as _ from 'lodash';
import {Apollo} from 'apollo-angular';
import {TemplateUtilsService} from '../../../shared/template-utils.service';
import {HttpClient} from '@angular/common/http';
import {ToastrService} from 'ngx-toastr';

const deleteExperiment = gql`
  mutation deleteExperiment($id: ID!){
    deleteExperiment(id: $id){
      id
    }
  }
`;

@Component({
  selector   : 'app-project-detail',
  templateUrl: './project-detail.component.html',
  styleUrls  : ['./project-detail.component.css']
})
export class ProjectDetailComponent implements OnInit {
  @ViewChild('groupModal') private groupModal: ModalDirective;
  @ViewChild('printAllModal') private printAllModal: ModalDirective;
  @ViewChild('deleteModal') private deleteModal: ModalDirective;
  private experiment: GQL.IExperiment;
  private accordionState: boolean [] = [];
  private groupToPrint: GQL.ISampleGroup = null;
  private showInputInformation = true;

  private deleteable = false;

  constructor(private route: ActivatedRoute, private http: HttpClient, private router: Router,
              private apollo: Apollo, private templateUtils: TemplateUtilsService, private toastr: ToastrService) {
  }

  ngOnInit() {
    if (this.route.children.length > 0) {
      this.showInputInformation = false;
    }
    this.experiment = this.route.snapshot.data['experiment']['data'];
    this.deleteable = !(this.experiment.timestamps.edges.length > 0);
    this.accordionState = Array(this.experiment.sampleGroups['edges'].length);
    _.fill(this.accordionState, false, 0, this.accordionState.length);
  }

  private onEdit() {
    this.router.navigate(['/edit', this.experiment.id])
  }

  private totalNumberOfPlants() {
    let count = 0;
    this.experiment.sampleGroups['edges'].forEach(group => {
      count += group.node.plants.edges.length;
    });
    return count;
  }

  private delete() {
    this.apollo.mutate({
        mutation : deleteExperiment,
        variables: {
          id: this.experiment.id
        }
      }
    ).subscribe(({data}) => {
      //TODO delete from apollo cache?
      this.router.navigate(['/projects']);
    }, (err) => {
      if (err.graphQLErrors.length > 0) {
        this.toastr.error(err.graphQLErrors[0].message)
      } else {
        this.toastr.error(err.message);
      }
    });
  }

  private confirmDelete() {
    this.deleteModal.hide();
    this.delete();
  }

  private printGroupEvent(group: GQL.ISampleGroup) {
    this.groupToPrint = group;
    this.groupModal.show();
  }

  private confirmPrintGroup(group: GQL.ISampleGroup) {
    this.groupModal.hide();
    this.printGroup(group);
  }

  private confirmPrintAll() {
    this.printAllModal.hide();
    this.experiment.sampleGroups['edges'].forEach(group => this.printGroup(group.node));
  }

  private printGroup(group: GQL.ISampleGroup) {
    this.http.post(environment.printEndpoint, {id: group.id}).subscribe(res => {
        console.log(res);
      },
      err => {
      //TODO use error message
        this.toastr.error('There was an error while trying to create the print job. Please try again later');
      });
  }


  tabClicked(event, timestamp: GQL.ITimestampEdge) {
    console.log(timestamp);
  }

  timestampClicked(event, timestampId: String) {
    this.showInputInformation = false;
    //setTimeout(() => this.router.navigate([timestampId], {relativeTo: this.route}), 0);
  }
}
