import { Component, inject } from '@angular/core';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-repository',
  standalone: true,
  template: `<section class="panel">
    <h2>Repozytorium danych</h2>
    <p>Lista pakietów będzie dostępna po zalogowaniu.</p>
    <p>{{ isAuthenticated ? 'Masz dostęp do pobierania plików.' : 'Aby pobierać pliki, zaloguj się.' }}</p>
  </section>`,
  styles: ['.panel{max-width:800px;margin:2rem auto;padding:2rem;border-radius:16px;background:white;box-shadow:0 10px 35px rgba(0,0,0,.12);}']
})
export class RepositoryComponent {
  private authService = inject(AuthService);
  isAuthenticated = this.authService.isAuthenticated();
}
