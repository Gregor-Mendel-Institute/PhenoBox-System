import {Directive, forwardRef, Inject} from '@angular/core';
import {NG_VALIDATORS, FormControl} from '@angular/forms';
import gql from 'graphql-tag/index';
import {Apollo} from 'apollo-angular';

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


export function uniqueExperimentNameValidatorFactory(apollo: Apollo) {
  return (c: FormControl) => {
    return new Promise(resolve => {
      if (c.value === '') {
        resolve(null);
      } else {
        apollo.query(
          {
            query    : getExperimentByName,
            variables: {
              name: c.value
            }
          }
        ).subscribe(({data}) => {
          if (data['experiments'].edges.length === 0) {
            resolve(null);
          } else {
            resolve({duplicateName: true})
          }
        });
      }
    });
  };
}

@Directive({
  selector : '[validate-sequence][ngModel],[validate-sequence][formControl]',
  providers: [
    {provide: NG_VALIDATORS, useExisting: forwardRef(() => UniqueExperimentNameValidatorDirective), multi: true}
  ]
})
export class UniqueExperimentNameValidatorDirective {

  validator: (c: FormControl) => Promise<{}>;

  constructor(apollo: Apollo) {
    this.validator = uniqueExperimentNameValidatorFactory(apollo);

  }

  validate(c: FormControl) {
    return this.validator(c);
  }
}
