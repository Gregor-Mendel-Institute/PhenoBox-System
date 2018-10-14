import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {AbstractControl, FormArray, FormBuilder, FormGroup, Validators} from '@angular/forms';
import {uniqueSampleGroupName} from './validators/unique-sample-group-name';
import {uniqueSampleGroupNameInput} from './validators/unique-sample-group-name-input';
import {UniqueExperimentNameValidatorDirective} from './validators/unique-experiment-name.validator';
import {environment} from '../../environments/environment';
import {PlantCountChangedEvent} from './sample-group/sample-group.component';
import {RemoveSampleGroupEvent} from './sample-group-list/sample-group-list.component';
import gql from 'graphql-tag';
import {Observable} from 'rxjs';
import {Apollo} from 'apollo-angular';
import {validateDates} from './validators/validate-dates.validator';
import * as moment from 'moment';
import {AddSampleGroupEvent} from './sample-group-input/sample-group-input.component';
import {AuthService} from '../login/auth.service';
import {singleControlGroup} from './validators/single-control-group.validator';

const getExperimentByName = gql`
  query getExperimentByName($name: String!){
    experiments(withName: $name) {
      edges {
        node {
          id
        }
      }
    }
  }
`;


@Component({
  selector   : 'app-project-form',
  templateUrl: './project-form.component.html',
  styleUrls  : ['./project-form.component.css'],
  providers  : [UniqueExperimentNameValidatorDirective]
})
export class ProjectFormComponent implements OnInit {

  @Input() experiment: GQL.IExperiment;
  @Output()
  submitted: EventEmitter<any> = new EventEmitter<any>(); //TODO type this
  project: FormGroup;
  numberOfPlants: number = 0;
  editing: boolean = false;
  restrictedEditing: boolean = false;

  constructor(private auth: AuthService, private fb: FormBuilder, private apollo: Apollo) {
  }

  ngOnInit() {
    let scientistName: string = '';
    let groupName: string = '';
    let id: string = '';
    let name: string = '';
    let description: string = '';
    let groups: FormGroup[] = [];
    let now: Date = new Date();
    now.setHours(0, 0, 0, 0);


    let startDate: string = now.toISOString();
    let startOfExperimentation: string = now.toISOString();

    if (this.experiment) {
      this.editing = true;
      this.restrictedEditing = this.experiment.timestamps.edges.length !== 0;
      id = this.experiment.id;
      name = this.experiment.name;
      description = this.experiment.description;
      scientistName = this.experiment.scientist;
      groupName = this.experiment.groupName;
      //Remark This timeshift hack is necessary due to the handling of timezones in the datepicker
      //Without this the date would shift one day back when not selected via the picker
      let d = new Date(moment.utc(this.experiment.startDate).local().toISOString());
      d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
      startDate = d.toISOString();
      if (this.experiment.startOfExperimentation) {
        d = new Date(moment.utc(this.experiment.startOfExperimentation).local().toISOString());
        d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
        startOfExperimentation = d.toISOString();
      } else {
        startOfExperimentation = "";
      }
      this.experiment.sampleGroups.edges.forEach(edge => {
        let group: GQL.ISampleGroup = edge.node;
        const formGroup = this.createSampleGroup(group);
        groups.push(formGroup);
      });
    } else {
      scientistName = this.auth.getUsername();
      groupName = this.auth.getGroup();
    }
  //TODO fix unique name input validator, add unique treatment validator
    this.project = this.fb.group({
      details           : this.fb.group({
        name         : [name, [Validators.required], [this.uniqueProjectNameValidator.bind(this)]],
        id           : [id],
        description  : [description],
        groupName    : [{value: groupName, disabled: true}, Validators.required],
        scientistName: [{value: scientistName, disabled: true}, Validators.required],
        dates        : this.fb.group({
          startDate             : [startDate, [Validators.required]],
          startOfExperimentation: [startOfExperimentation],
          additionalDate        : [false]
        }, {validator: validateDates})
      }),
      sampleGroupDetails: this.fb.group({
        sampleCount         : [environment.defaultSampleCount, Validators.required],
        sampleGroupNameInput: [''],
        isControlGroupInput : [false],
        treatmentInput      : [''],
      }),
      sampleGroups      : this.fb.array(groups,
        Validators.compose([singleControlGroup, uniqueSampleGroupName, Validators.required]))
    }, {validator: uniqueSampleGroupNameInput});
    this.numberOfPlants = this.totalNumberOfPlants();
  }

  private uniqueProjectNameValidator(control: AbstractControl) {
    //Don'T send requests for an empty name and if the user is editing a project it should be possible to use the original name
    if (control.value.trim() === '' || (this.editing && control.value === this.experiment.name)) {
      return Observable.of(null);
    }
    //Throttle this?

    return this.apollo.query(
      {
        query    : getExperimentByName,
        variables: {
          name: control.value
        }
      }
    ).map(response => response.data['experiments'].edges)
      .map((results: any[]) => !!results.length)
      .map((result: boolean) => result ? {'duplicateName': true} : null)
  }

  private onRemoveSampleGroup({index}: RemoveSampleGroupEvent) {
    (this.project.get('sampleGroups') as FormArray).removeAt(index);
    this.numberOfPlants = this.totalNumberOfPlants();
  }

  private addSampleGroup(payload: AddSampleGroupEvent) {
    let sampleCount = payload.sampleCount;
    let group: GQL.ISampleGroupInput = {
      name     : payload.name,
      treatment: payload.treatment,
      isControl: payload.isControl
    };
    (this.project.get('sampleGroups') as FormArray).push(this.createNewSampleGroup(group, sampleCount));
    this.numberOfPlants = this.totalNumberOfPlants();

  }

  /**
   * Creates FormGroup for the given Sample Group
   * @param {GQL.ISampleGroup} group Data of the given group
   * @returns {FormGroup}
   */
  private createSampleGroup(group: GQL.ISampleGroup): FormGroup {
    let plantControls: FormGroup[] = [];

    group.plants['edges'].forEach((edge) => {
      let plant = edge['node'];
      plantControls.push(this.createPlant(plant.index, plant.name, plant.id));
    });

    return this.fb.group({
      id                    : [group.id],
      sampleGroupName       : [group.name, [Validators.required]],
      sampleGroupDescription: [group.description],
      isControl             : [group.isControl],
      plantCount            : [plantControls.length],
      species               : [group.species],
      variety               : [group.variety],
      genotype              : [group.genotype],
      growthConditions      : [group.growthConditions],
      treatment             : [group.treatment, [Validators.required]],
      plants                : this.fb.array(plantControls)
    });
  }

  private createNewSampleGroup({name, treatment, isControl, description = '', species = '', variety = '', genotype = '', growthConditions = ''}: GQL.ISampleGroupInput, newSampleCount: number = 0): FormGroup {
    let plantControls: FormGroup[] = [];

    if (newSampleCount > 0) {//Initialize blank plants
      for (let i = 0; i < newSampleCount; i++) {
        plantControls.push(this.createPlant(i + 1))
      }
    }
    return this.fb.group({
      id                    : [''],
      sampleGroupName       : [name, [Validators.required]],
      sampleGroupDescription: [description],
      isControl             : [isControl],
      plantCount            : [plantControls.length],
      species               : [species],
      variety               : [variety],
      genotype              : [genotype],
      growthConditions      : [growthConditions],
      treatment             : [treatment, [Validators.required]],
      plants                : this.fb.array(plantControls)
    });
  }

  private onPlantCountChanged({formGroupName, oldCount, newCount}: PlantCountChangedEvent) {
    let plants = this.project.get(`sampleGroups.${formGroupName}.plants`) as FormArray;
    console.log("CountChanged");
    if (oldCount > newCount) {
      for (let i = oldCount - 1; i >= newCount; i--) {
        plants.removeAt(i);
      }
    } else {
      for (let i = oldCount; i < newCount; i++) {
        plants.push(this.createPlant(plants.length + 1))
      }
    }
    this.numberOfPlants = this.totalNumberOfPlants();
  }


  createPlant(index: number, name: string = '', id: string = ''): FormGroup {
    return this.fb.group({
      id   : [id],
      index: [index],
      name : [name, [Validators.maxLength(environment.plantNameMaxLength)]]
    });
  }

  private totalNumberOfPlants() {
    let count = 0;
    (this.project.get('sampleGroups') as FormArray).value.forEach(group => {
      count += group.plants.length;
    });
    return count;
  }

  private onSubmit() {
    console.log('submit', this.project);
    if (this.project.valid) {
      //Remark: the datePicker uses Timezone offsets so one must add the timezone offset when using the value,
      //otherwise it could result in wrong dates
      let start = new Date(this.project.get('details.dates.startDate').value);
      start.setMinutes(start.getMinutes() + start.getTimezoneOffset());
      start.setHours(0, 0, 0, 0);
      let expDate = null;
      if (this.project.get('details.dates.startOfExperimentation').value) {
        expDate = new Date(this.project.get('details.dates.startOfExperimentation').value);
        expDate.setMinutes(expDate.getMinutes() + expDate.getTimezoneOffset());
        expDate.setHours(0, 0, 0, 0);
      }
      console.log(start);
      console.log(expDate);
      this.project.get('details.dates').patchValue(
        {startDate: start.toISOString()});
      if (expDate) {
        this.project.get('details.dates').patchValue(
          {startOfExperimentation: expDate.toISOString()});

      }
      console.log('raw', this.project.getRawValue());
      this.submitted.emit(this.project.getRawValue());
    }
  }
}
