import {Injectable} from '@angular/core';
import {Router, RouterStateSnapshot, ActivatedRouteSnapshot} from '@angular/router';
import {CanActivate} from '@angular/router';
import {AuthService} from './auth.service';

@Injectable()
export class AuthGuard implements CanActivate {

  constructor(private auth: AuthService, private router: Router) {
  }

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): boolean {
    let url: string = state.url;
    return this.checkLogin(url);
  }

  checkLogin(url: string): boolean {
    if (this.auth.loggedIn()) {
      this.auth.caughtByGuard = false;
      return true;
    }
    this.auth.redirectUrl = url; // set url in authService here
    this.auth.assertCaughtByGuard();
    this.router.navigate(['/login']);

    return false;
  }
}
