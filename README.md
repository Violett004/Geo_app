# Geo_app
# System Monitoringu Przyrodniczo-Ekologicznego

Aplikacja webowa (FastAPI + Angular) do automatycznego pozyskiwania, przetwarzania (ETL) oraz udostępniania danych przestrzennych (GeoJSON, CSV, ZIP) o walorach turystycznych i jakości powietrza w Polsce.

---

## Technologie

* **Backend:** Python 3.11, FastAPI, SQLAlchemy (SQLite), APScheduler
* **Frontend:** Angular 17+ (Standalone Components), Leaflet.js (Mapa interaktywna)
* **API zewnętrzne:** Overpass API (OpenStreetMap), GIOŚ API

---

## Szybkie Uruchomienie

### 1. Backend (FastAPI)
```bash
# Instalacja zależności
pip install -r requirements.txt

# Uruchomienie serwera (port 8001)
python main.py

cd frontend

# Instalacja pakietów npm
npm install

# Uruchomienie aplikacji (port 4200)
ng serve --open

npm start
