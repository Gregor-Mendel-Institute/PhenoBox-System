import {Component, Input, OnInit} from '@angular/core';
import {FormArray, FormGroup} from '@angular/forms';
import {environment} from '../../../environments/environment';

@Component({
  selector   : 'plant-list',
  templateUrl: './plant-list.component.html',
  styleUrls  : ['./plant-list.component.css']
})
export class PlantListComponent implements OnInit {


  @Input() parent: FormGroup;
  private self: FormArray;
  private plantNameMaxLength: number;

  constructor() {
    this.plantNameMaxLength = environment.plantNameMaxLength;
  }

  ngOnInit() {
    this.self = <FormArray>this.parent.get('plants');
  }

  computeIndices(): number[] {
    return Array(Math.ceil(this.self['controls'].length / 2)).fill(0).map((x, i) => i * 2);
  }

}
