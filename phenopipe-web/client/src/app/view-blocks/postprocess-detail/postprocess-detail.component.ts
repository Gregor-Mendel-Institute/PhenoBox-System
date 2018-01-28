import {Component, Input, OnInit} from '@angular/core';
import {TemplateUtilsService} from '../../shared/template-utils.service';

@Component({
  selector   : 'app-postprocess-detail',
  templateUrl: './postprocess-detail.component.html',
  styleUrls  : ['./postprocess-detail.component.css']
})
export class PostprocessDetailComponent implements OnInit {

  @Input()
  postprocess: GQL.IPostprocess;

  constructor(private templateUtils: TemplateUtilsService) {
  }

  ngOnInit() {
  }

}
