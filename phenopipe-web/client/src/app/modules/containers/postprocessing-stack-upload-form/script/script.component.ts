import {Component, Input, OnInit, OnChanges, SimpleChanges} from '@angular/core';
import {FormGroup} from '@angular/forms';

@Component({
  selector: 'app-script',
  templateUrl: './script.component.html',
  styleUrls: ['./script.component.css']
})
export class ScriptComponent implements OnInit {


  @Input()
  parent: FormGroup;
  @Input()
  formGrName: string;

  private self: FormGroup;
  constructor() { }

  ngOnInit() {
    this.self = <FormGroup>this.parent.get('' + this.formGrName);
  }


}
