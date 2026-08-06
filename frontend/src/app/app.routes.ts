import { Routes } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { MapComponent } from './components/map/map.component';
import { RepositoryComponent } from './components/repository/repository.component';
import { DocumentationComponent } from './components/documentation/documentation.component';
import { AuthorComponent } from './components/author/author.component';
import { AuthComponent } from './components/auth/auth.component';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'mapa', component: MapComponent },
  { path: 'repozytorium', component: RepositoryComponent, canActivate: [authGuard] },
  { path: 'dokumentacja', component: DocumentationComponent },
  { path: 'autorzy', component: AuthorComponent },
  { path: 'login', component: AuthComponent },
  { path: '**', redirectTo: '' }
];