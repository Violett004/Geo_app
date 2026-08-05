import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './auth.component.html',
  styleUrls: ['./auth.component.css']
})
export class AuthComponent {
  private fb = inject(FormBuilder);
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  private authService = inject(AuthService);

  authForm: FormGroup;
  isLoginMode = true;
  errorMessage = '';
  private readonly redirectUrl = this.route.snapshot.queryParamMap.get('redirect') ?? '/';

  constructor() {
    this.authForm = this.fb.group({
      username: ['', Validators.required],
      password: ['', [Validators.required, Validators.minLength(6)]],
      email: ['']
    });
  }

  toggleMode(): void {
    this.isLoginMode = !this.isLoginMode;
    this.errorMessage = '';
    this.authForm.reset({
      username: this.authForm.value.username ?? '',
      password: this.authForm.value.password ?? '',
      email: this.authForm.value.email ?? ''
    });
    if (!this.isLoginMode) {
      this.authForm.get('email')?.setValidators([Validators.required, Validators.email]);
    } else {
      this.authForm.get('email')?.clearValidators();
    }
    this.authForm.get('email')?.updateValueAndValidity();
  }

  submit(): void {
    if (this.authForm.invalid) {
      this.errorMessage = 'Uzupełnij poprawnie formularz.';
      return;
    }

    const { username, password, email } = this.authForm.value;

    if (this.isLoginMode) {
      this.authService.login(username, password).subscribe({
        next: (response) => {
          this.authService.setCurrentUser(response.user ?? { username });
          this.router.navigateByUrl(this.redirectUrl);
        },
        error: (error) => {
          this.errorMessage = error?.error?.detail || 'Nieprawidłowy login lub hasło.';
        }
      });
      return;
    }

    this.authService.register(username, email, password).subscribe({
      next: (response) => {
        this.authService.setCurrentUser(response.user ?? { username, email });
        this.router.navigateByUrl(this.redirectUrl);
      },
      error: (error) => {
        this.errorMessage = error?.error?.detail || 'Nie udało się utworzyć konta.';
      }
    });
  }
}
