import {Component, OnInit} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import gql from 'graphql-tag';
import * as _ from 'lodash';
import {Apollo} from 'apollo-angular';
import {ToastrService} from 'ngx-toastr';

const editProject = gql`
  mutation editProject($projectData:EditProjectInput!){
    editProject(projectData: $projectData)
    {
      experiment{id
        name
        description
        scientist
        groupName
        createdAt
        updatedAt
        sampleGroups{
          edges{
            node{
              name
              description
              isControl
              treatment
              species
              variety
              genotype
              growthConditions
              id
              plants{
                edges{
                  node{
                    id
                    name
                  }
                }
              }
            }
          }
        }
        timestamps{
          edges{
            node{
              id
            }
          }
        }
      }
    }
  }
`;

@Component({
  selector   : 'app-edit-project',
  templateUrl: './edit-project.component.html',
  styleUrls  : ['./edit-project.component.css']
})
export class EditProjectComponent implements OnInit {

  private experiment: GQL.IExperiment;

  constructor(private route: ActivatedRoute, private router: Router, private apollo: Apollo, private toastr: ToastrService) {
  }

  ngOnInit() {
    this.experiment = this.route.snapshot.data['experiment']['data'];
  }

  editProject(project) {
    let sampleGroupsPayload: GQL.IEditSampleGroupInput[] = [];
    let oldGroups = this.experiment.sampleGroups.edges.map((group) => group.node);
    let diff = _.differenceWith(oldGroups, project.sampleGroups,
      (old: GQL.ISampleGroup, curr: GQL.ISampleGroup) => old.id === curr.id);
    //Mark deleted groups
    diff.forEach((group) => {
      sampleGroupsPayload.push({id: group.id, treatment: group.treatment, delete: true});
    });

    //Process remaining Groups
    project.sampleGroups.forEach(group => {
      let plantData: GQL.IEditPlantInput[] = [];

      let oldGroup = _.find(oldGroups, (old) => {
        return group.id === old.id;
      });
      if (oldGroup) {
        let diff = _.differenceWith(oldGroup.plants.edges, group.plants, (old: GQL.IPlantEdge, curr: GQL.IPlant) => {
          return old.node.id === curr.id;
        });
        //Mark deleted plants
        diff.forEach((plant: GQL.IPlantEdge) => {
          plantData.push({id: plant.node.id, index: plant.node.index, delete: true});
        });
      }
      group.plants.forEach((plant) => {
        plantData.push({id: plant.id, index: plant.index, name: plant.name})
      });
      let groupData: GQL.IEditSampleGroupInput = {
        id              : group.id,
        name            : group.sampleGroupName,
        description     : group.sampleGroupDescription,
        isControl       : group.isControl,
        species         : group.species,
        variety         : group.variety,
        genotype        : group.genotype,
        growthConditions: group.growthConditions,
        treatment       : group.treatment,
        plants          : plantData
      };
      sampleGroupsPayload.push(groupData);
    });
    let payload: GQL.IEditProjectInput = {
      id                    : project.details.id,
      name                  : project.details.name,
      description           : project.details.description,
      scientist             : project.details.scientist,
      groupName             : project.details.groupName,
      startDate             : project.details.dates.startDate,
      startOfExperimentation: project.details.dates.startOfExperimentation,
      sampleGroupData       : sampleGroupsPayload
    };

    this.apollo.mutate({
      mutation : editProject,
      variables: {
        projectData: payload
      }
    }).subscribe(({data}) => {
        this.router.navigate(['/projects', project.details.id]);
    }, (err) => {
      if (err.graphQLErrors.length > 0) {
        this.toastr.error(err.graphQLErrors[0].message)
      } else {
        this.toastr.error(err.message);
      }
    });
  }
}
