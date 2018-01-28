import {Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges} from '@angular/core';

@Component({
  selector   : 'app-stack-selector',
  templateUrl: './stack-selector.component.html',
  styleUrls  : ['./stack-selector.component.css']
})
export class StackSelectorComponent implements OnInit, OnChanges {


  @Input()
  postprocessingStacks: GQL.IPostprocessingStackEdge[];
  @Output()
  onStackClicked: EventEmitter<GQL.IPostprocessingStack> = new EventEmitter<GQL.IPostprocessingStack>();

  selectedStacks: GQL.IPostprocessingStackEdge[] = [];
  availableStacks: GQL.IPostprocessingStackEdge[] = [];

  constructor() {
  }

  ngOnInit() {
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['postprocessingStacks']) {

      this.availableStacks = [];
      this.selectedStacks = [];
      if (changes['postprocessingStacks'].currentValue != null) {
        changes['postprocessingStacks'].currentValue.forEach((stack) => {
          this.availableStacks.push(Object.assign({}, stack));
        });
        this.availableStacks.sort(this.stackComparator);
      }
    }
  }

  private stackComparator(a: GQL.IPostprocessingStackEdge, b: GQL.IPostprocessingStackEdge) {
    let a_n = a.node.name.toLowerCase();
    let b_n = b.node.name.toLowerCase();
    if (a_n < b_n) {
      return -1;
    }
    if (a_n > b_n) {
      return 1;
    }
    return 0;

  }

  stackClicked(event, stack: GQL.IPostprocessingStackEdge) {
    this.onStackClicked.emit(stack.node);
  }

  transferToSelected(stack) {
    this.selectedStacks.sort(this.stackComparator);
    this.onStackClicked.emit(stack.node);
  }

  transferToAvailable(stack) {
    this.availableStacks.sort(this.stackComparator);
  }
}
