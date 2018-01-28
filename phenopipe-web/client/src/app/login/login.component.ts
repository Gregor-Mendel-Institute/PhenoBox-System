import {Component, OnInit} from '@angular/core';
import {AuthService} from './auth.service';
import {FormBuilder, Validators, FormGroup} from '@angular/forms';
import {ActivatedRoute} from '@angular/router';

interface User {
  name: string;
  password: string;
}

@Component({
  selector   : 'app-login',
  templateUrl: './login.component.html',
  styleUrls  : ['./login.component.css']
})
export class LoginComponent implements OnInit {

  user: FormGroup;
  constructor(private auth: AuthService, private fb: FormBuilder) {
  }

  ngOnInit() {
    this.user = this.fb.group({
      name    : ['', [Validators.required]],
      password: ['', [Validators.required]]
    });
  }

  onSubmit({value, valid}: {value: User, valid: boolean}) {
    this.auth.clearFlags();
    this.auth.login(value.name, value.password)
  }

}
