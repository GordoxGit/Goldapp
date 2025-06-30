# GoldMarket Live
![Backend CI](https://github.com/<ORG_OR_USER>/Goldapp/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)

> **Version 0.1.0 — MVP backend en cours**

Application Android + backend FastAPI qui affiche en **notification permanente** les indicateurs macro
impactant directement le cours de l’or.

## 📐 Architecture

| Couche                   | Tech                        | Rôle                                                              |
| ------------------------ | --------------------------- | ----------------------------------------------------------------- |
| **Backend**              | FastAPI + Python 3.10       | Agrège & normalise les données (yfinance, BLS, BEA, FRED bientôt) |
| **Notification Service** | Kotlin + ForegroundService  | Affiche les indicateurs mis à jour toutes 30 s                    |
| **VPS**                  | Debian 12 + systemd + Nginx | Héberge le backend 24/7                                           |

```
Android (Retrofit) ─┐                     
                   │ /api/v1/*           
         Nginx ───► FastAPI (Gunicorn)──► yfinance / BLS / BEA / (FRED)
```

## 🗂️ Repo layout (MVP)

```
Goldapp/
├─ backend/
│  ├─ app/
│  │  ├─ __init__.py
│  │  ├─ main.py          # point d'entrée FastAPI
│  │  ├─ crud.py          # appels externes + cache
│  │  ├─ schemas.py       # modèles Pydantic
│  │  └─ config.py        # lecture .env
│  ├─ requirements.txt
│  └─ .env.example        # gabarit variables d'environnement
└─ README.md              # ce fichier
```

## 🚀 Lancer le backend localement

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload  # http://127.0.0.1:8000/docs
```

Le cache interne peut être ajusté via la variable `TTL` dans un fichier `.env` placé à la racine de `backend/`. Par défaut, les données sont conservées 300 s.

### `.env` (exemple)

```
# clés officielles (facultatives pour le MVP)
BLS_API_KEY=xxxxxxxxxxxxxxxx
BEA_API_KEY=xxxxxxxxxxxxxxxx
# FRED_API_KEY=xxxxxxxxxxxxxxxx  # sera ajouté plus tard
```

## 📡 Endpoints disponibles (MVP)

| Route                    | Méthode | Description                                       |
| ------------------------ | ------- | ------------------------------------------------- |
| `/api/v1/market_indices` | GET     | Retourne **DXY (UUP)** et **Volume US** (SPY+QQQ) |
| `/api/v1/latest_macro`   | GET     | Dernière statistique CPI ou NFP publiée |
| `/api/v1/pce`            | GET     | Variation mensuelle du PCE |
| `/api/v1/fed_rate`       | GET     | Dernier taux directeur de la FED |
| `/api/v1/vix`            | GET     | Clôture quotidienne du VIX |
| `/api/v1/fomc_next`      | GET     | Prochaine réunion FOMC |

Exemple de réponse :

```json
{
  "date": "2024-07-31",
  "time": "18:00",
  "title": "FOMC Meeting",
  "url": "https://www.federalreserve.gov/..."
}
```

## 🛠️ Build & déploiement VPS

1. Copier le dossier **backend/** sur le serveur.
2. Créer un service **systemd** (voir `deploy/goldapp.service` à venir).
3. Brancher Nginx en reverse‑proxy (port 80).

## ✅ Feuille de route courte

* [x] Ticket #1 — Base FastAPI + endpoint market\_indices (yfinance)
* [x] Ticket #2 — Endpoints CPI/NFP (BLS)
* [x] Ticket #3 — Endpoint PCE (BEA)
* [x] Ticket #4 — Endpoints FED rate & VIX (FRED)
* [ ] Ticket #5 — Service systemd + Nginx conf
* [ ] Ticket #6 — Android ForegroundService & UI Compose

## 📝 Licence

Projet sous licence **MIT** (voir fichier `LICENSE`).
