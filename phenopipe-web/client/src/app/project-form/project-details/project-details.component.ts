import {Component, Input, OnInit} from '@angular/core';
import {FormGroup} from '@angular/forms';

@Component({
  selector   : 'app-project-details',
  templateUrl: './project-details.component.html',
  styleUrls  : ['./project-details.component.css'],
})
export class ProjectDetailsComponent implements OnInit {

  @Input()
  parent: FormGroup;

  self: FormGroup;

  constructor() {
  }

  ngOnInit() {
    this.self = <FormGroup>this.parent.get('details');
    this.self.get('dates.startDate').valueChanges.subscribe((date) => {
      if (!this.self.get('dates.additionalDate').value) {
        this.self.get('dates').patchValue({startOfExperimentation: date});
      }
    });
    this.self.get('dates.additionalDate').valueChanges.subscribe((isSame) => {
      this.self.get('dates').patchValue({startOfExperimentation: this.self.get('dates.startDate').value});
    })
  }

}
