import {Component, Input, OnInit} from '@angular/core';
import {TemplateUtilsService} from '../../shared/template-utils.service';
//TODO Create graphql fragment here to define the fields needed in this component
@Component({
  selector   : 'app-analysis-detail',
  templateUrl: './analysis-detail.component.html',
  styleUrls  : ['./analysis-detail.component.css']
})
export class AnalysisDetailComponent implements OnInit {

  @Input()
  analysis: GQL.IAnalysis;

  constructor(private templateUtils: TemplateUtilsService) {
  }

  ngOnInit() {
  }

}
