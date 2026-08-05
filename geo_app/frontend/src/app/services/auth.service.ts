import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private readonly storageKey = 'geo-current-user';
  private currentUserSubject = new BehaviorSubject<any | null>(this.loadStoredUser());
  currentUser$ = this.currentUserSubject.asObservable();

  login(username: string, password: string): Observable<any> {
    return this.http.post('/api/auth/login', { username, password });
  }

  register(username: string, email: string, password: string): Observable<any> {
    return this.http.post('/api/auth/register', { username, email, password });
  }

  setCurrentUser(user: any | null): void {
    if (user) {
      localStorage.setItem(this.storageKey, JSON.stringify(user));
    } else {
      localStorage.removeItem(this.storageKey);
    }
    this.currentUserSubject.next(user);
  }

  getCurrentUser(): any | null {
    return this.currentUserSubject.getValue();
  }

  isAuthenticated(): boolean {
    return !!this.getCurrentUser();
  }

  logout(): void {
    this.setCurrentUser(null);
  }

  private loadStoredUser(): any | null {
    if (typeof window === 'undefined' || typeof localStorage === 'undefined') {
      return null;
    }

    const stored = localStorage.getItem(this.storageKey);
    return stored ? JSON.parse(stored) : null;
  }
}
