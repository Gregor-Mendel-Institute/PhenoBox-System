import {Component, OnInit} from '@angular/core';
import gql from 'graphql-tag/index';
import {Router} from '@angular/router';

import {Apollo} from 'apollo-angular';
import {AuthService} from '../../../login/auth.service';
import {ToastrService} from 'ngx-toastr';

const constructExperiment = gql`
  mutation constructExperiment($experimentData:ExperimentInput!){
    constructExperiment(experimentData: $experimentData)
    {
      id
    }
  }
`;


@Component({
  selector   : 'app-create-project',
  templateUrl: './create-project.component.html',
  styleUrls  : ['./create-project.component.css']
})
export class CreateProjectComponent implements OnInit {
  constructor(private auth: AuthService, private apollo: Apollo, private router: Router, private toastr: ToastrService) {
  }

  ngOnInit() {
  }

  createProject(project) {
    console.log('submitted project', project);
    let sampleGroupsPayload: GQL.ISampleGroupInput[] = [];
    //for (let group of project.sampleGroups) {
    project.sampleGroups.forEach(group => {
      let plantData: GQL.IPlantInput[] = [];
      group.plants.forEach((plant, i) => {
        plantData.push({index: plant.index, name: plant.name})
      });
      let groupData: GQL.ISampleGroupInput = {
        name            : group.sampleGroupName,
        description     : group.sampleGroupDescription,
        isControl       : group.isControl,
        treatment       : group.treatment,
        species         : group.species,
        variety         : group.variety,
        growthConditions: group.growthConditions,
        genotype        : group.genotype,
        plants          : plantData
      };
      sampleGroupsPayload.push(groupData);
    });
    let payload: GQL.IExperimentInput = {
      name                  : project.details.name,
      description           : project.details.description,
      scientist             : this.auth.getUsername(),
      groupName             : project.details.groupName,
      startDate             : project.details.dates.startDate,
      startOfExperimentation: project.details.dates.startOfExperimentation,
      sampleGroupData       : sampleGroupsPayload
    };
    console.log('exp payload', payload);
    this.apollo.mutate({
      mutation : constructExperiment,
      variables: {
        experimentData: payload
      }
    }).subscribe(({data}) => {
      this.router.navigate(['/projects', data['constructExperiment']['id']]);
    }, (err) => {
      if (err.graphQLErrors.length > 0) {
        this.toastr.error(err.graphQLErrors[0].message)
      } else {
        this.toastr.error(err.message);
      }
    });

  }

}
