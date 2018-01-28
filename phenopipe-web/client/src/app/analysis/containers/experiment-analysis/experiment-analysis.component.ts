import { Component, OnInit } from '@angular/core';
import {ActivatedRoute} from '@angular/router';

@Component({
  selector: 'app-experiment-analysis',
  templateUrl: './experiment-analysis.component.html',
  styleUrls: ['./experiment-analysis.component.css']
})
export class ExperimentAnalysisComponent implements OnInit {

  private experiment_id;
  constructor(private route: ActivatedRoute) {
    route.params.subscribe(params => this.experiment_id = params.experiment_id);
  }

  ngOnInit() {
    console.log(this.experiment_id);
  }


}
