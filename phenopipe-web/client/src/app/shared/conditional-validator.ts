import {Observable} from 'rxjs';
import {FormControl, AbstractControl} from '@angular/forms';

type IsActiveFn = (parent: AbstractControl)=>Observable<boolean>;
type IsActiveObs=Observable<boolean>;
type Validator = (c: FormControl)=>any;
export class ConditionalValidator {

    private _isActivated: boolean;


    static create(validator: Validator, isActiveConditional: IsActiveObs | IsActiveFn) {
        let conditionalValidator = new this(validator, isActiveConditional);
        return conditionalValidator._getValidator();
    }

    constructor(private validator: (c: FormControl)=>any, private isActiveConditional: IsActiveObs | IsActiveFn) {
        this._isActivated = true;
    }

    private createSubscription(c: FormControl, obs: Observable<boolean>) {
        obs.subscribe(active => {
            this._isActivated = active;
            c.updateValueAndValidity({emitEvent:false});
        });
    }

    private _getValidator() {
        let initialized: boolean = false;
        return (control: FormControl)=> {
            //When the validator is called the first time the FormGroup might not be initialized completely thus the control has no parent
            //For proper initialization we need the parent FormGroup|FormArray
            if (!initialized) {
                if (typeof this.isActiveConditional === 'function' && control.root !== control) {
                    initialized = true;
                    let isActiveObs: IsActiveObs = (<IsActiveFn>this.isActiveConditional)(control.root);
                    this.createSubscription(control, isActiveObs);

                } else if (this.isActiveConditional instanceof Observable) {
                    initialized = true;
                    this.createSubscription(control, <Observable<boolean>>this.isActiveConditional);
                }
            }

            if (this._isActivated) {
                return this.validator(control);
            } else {
                return null;
            }
        };
    }
}
