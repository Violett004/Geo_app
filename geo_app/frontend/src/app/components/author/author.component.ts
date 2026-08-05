import { Component } from '@angular/core';

@Component({
  selector: 'app-author',
  standalone: true,
  template: `<section class="panel"><h2>Autorzy</h2><p>Projekt Geo App.</p></section>`,
  styles: ['.panel{max-width:800px;margin:2rem auto;padding:2rem;border-radius:16px;background:white;box-shadow:0 10px 35px rgba(0,0,0,.12);}']
})
export class AuthorComponent {}
