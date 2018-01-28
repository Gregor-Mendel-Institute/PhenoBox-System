import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {FormArray, FormGroup} from '@angular/forms';

@Component({
  selector: 'app-script-list',
  templateUrl: './script-list.component.html',
  styleUrls: ['./script-list.component.css']
})
export class ScriptListComponent implements OnInit {

  @Input()
  parent : FormGroup;
  @Output()
  scriptSelected : EventEmitter<number> = new EventEmitter<number>();
  private self : FormArray;

  constructor() { }

  ngOnInit() {
    this.self = <FormArray>this.parent.get('scripts')
  }

  private scriptClicked(group, index){
    this.scriptSelected.emit(index);
  }

}
