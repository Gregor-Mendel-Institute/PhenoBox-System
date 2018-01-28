import {Injectable} from '@angular/core';
import {environment} from '../../environments/environment';
import {Router} from '@angular/router';
import {HttpClient, HttpHeaders} from '@angular/common/http';

@Injectable()
export class AuthService {
  redirectUrl: string = '/projects'; //Gets set by the AuthGuard in case it must redirect
  caughtByGuard: boolean = false;
  invalidCredentials: boolean = false;
  refreshSubscription: any;

  constructor(public http: HttpClient, private router: Router) {
  }


  wasCaughtByGuard() {
    return this.caughtByGuard;
  }

  suppliedInvalidCredentials() {
    return this.invalidCredentials;
  }

  clearFlags() {
    this.caughtByGuard = false;
    this.invalidCredentials = false;
  }

  assertCaughtByGuard() {
    this.caughtByGuard = true;
    this.invalidCredentials = false;
  }

  loggedIn() {
    return !!localStorage.getItem('id_token');
  }

  getFullName() {
    let user_info = JSON.parse(localStorage.getItem('user_info'));

    return user_info.name + ' ' + user_info.surname;
  }

  getUsername() {
    let user_info = JSON.parse(localStorage.getItem('user_info'));
    return user_info.username;
  }

  getGroup() {
    let user_info = JSON.parse(localStorage.getItem('user_info'));
    return user_info.groups[0];
  }

  public getNewJwt() {
    let refreshToken = localStorage.getItem('refresh_token');

    const headers = new HttpHeaders()
      .set('Content-Type', 'application/json')
      .set('Authorization', 'Bearer ' + refreshToken);
    this.http.post<{ access_token: string; }>(environment.baseUrl + environment.reauthEndpoint, {headers})
      .subscribe(
        (res) => {
          localStorage.setItem('id_token', res.access_token)
        }, (err) => {
          alert('There was an error while trying to authenticate. Please try again later'); //TODO use toastr
        });
  }

  login(username: string, password: string) {
    this.http.post<{ access_token: string; refresh_token: string; user_info: { [key: string]: any } }>(
      environment.authEndpoint,
      {username: username, password: password})
      .subscribe((res) => {
          console.log(res);
          localStorage.setItem('id_token', res.access_token);
          localStorage.setItem('refresh_token', res.refresh_token);
          localStorage.setItem('user_info', JSON.stringify(res.user_info));
          //this.apollo.getClient().resetStore();
          this.invalidCredentials = false;
          //this.scheduleRefresh();
          this.redirect();
        },
        (err) => {
          if (err.status === 401) { //Unauthorized
            console.log('unauthorized');
            this.invalidCredentials = true;
          }
          console.log('error', err)
        });
  }

  logout() {
    localStorage.removeItem('id_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_info');

    this.router.navigate(['/login'])
  }

  private redirect(): void {
    console.log('redirect URL', this.redirectUrl);
    this.router.navigate([this.redirectUrl]); //use the stored url here
  }
}
