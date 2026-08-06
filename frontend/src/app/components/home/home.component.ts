import { Component, inject } from '@angular/core';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <section class="home-card">
      <h2>Witaj w Geo App</h2>
      <p>System działa poprawnie po stronie Angulara i backendu.</p>
      <div class="actions">
        <a routerLink="/mapa">Mapa</a>
        <a routerLink="/repozytorium">Repozytorium</a>
        <a routerLink="/dokumentacja">Dokumentacja</a>
        <a routerLink="/autorzy">Autorzy</a>
      </div>
    </section>
  `,
  styles: [
    `.home-card { max-width: 700px; margin: 2rem auto; padding: 2rem; border-radius: 16px; background: white; box-shadow: 0 10px 35px rgba(0,0,0,.12);} .actions { display:flex; flex-wrap:wrap; gap: 0.75rem; margin-top: 1rem;} .actions a { text-decoration:none; padding:0.7rem 1rem; border-radius:999px; background:#e2e8f0; color:#0f172a; }`
  ]
})
export class HomeComponent {}
