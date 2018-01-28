import {Component, OnInit, ViewChild} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {TemplateUtilsService} from '../../../shared/template-utils.service';
import gql from 'graphql-tag/index';
import * as _ from 'lodash';
import {AuthService} from '../../../login/auth.service';

const deleteExperiment = gql`
  mutation deleteExperiment($id: ID!){
    deleteExperiment(id: $id){
      id
    }
  }
`;

@Component({
  selector   : 'app-project-dashboard',
  templateUrl: './project-dashboard.component.html',
  styleUrls  : ['./project-dashboard.component.css']
})
export class ProjectDashboardComponent implements OnInit {

  @ViewChild('projectsTable') private table: any;
  private projects: GQL.IExperimentEdge[];

  constructor(private route: ActivatedRoute, private router: Router, private auth: AuthService, private templateUtils: TemplateUtilsService) {
  }

  ngOnInit() {
    console.log(this.route.snapshot.data['experiments']['data']);
    this.projects = <GQL.IExperimentEdge[]>_.sortBy(this.route.snapshot.data['experiments']['data']['edges'],
      edge => edge.node.name.toLowerCase());

  }

  private onActivate(event) {
    if (event.type == 'click') {
      this.router.navigate(['/projects', event.row.node.id])
    }
  }
}
