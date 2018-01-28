import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {AnalysisDetailComponent} from './analysis-detail/analysis-detail.component';
import {PostprocessDetailComponent} from './postprocess-detail/postprocess-detail.component';
import {SharedModule} from '../shared/shared.module';

@NgModule({
  imports     : [
    CommonModule,
    SharedModule
  ],
  declarations: [
    AnalysisDetailComponent,
    PostprocessDetailComponent
  ],
  exports     : [
    AnalysisDetailComponent, PostprocessDetailComponent
  ]
})
export class ViewBlocksModule {
}
