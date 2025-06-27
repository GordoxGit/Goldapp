# GoldMarket Live
![Backend CI](https://github.com/<ORG_OR_USER>/Goldapp/actions/workflows/ci.yml/badge.svg)

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

`/api/v1/fed_rate`, `/api/v1/vix`, `/api/v1/latest_macro` … seront ajoutés dans les tickets suivants.

## 🛠️ Build & déploiement VPS

1. Copier le dossier **backend/** sur le serveur.
2. Créer un service **systemd** (voir `deploy/goldapp.service` à venir).
3. Brancher Nginx en reverse‑proxy (port 80).

## ✅ Feuille de route courte

* [x] Ticket #1 — Base FastAPI + endpoint market\_indices (yfinance)
* [ ] Ticket #2 — Endpoints CPI/NFP (BLS)
* [ ] Ticket #3 — Endpoint PCE (BEA)
* [ ] Ticket #4 — Endpoints FED rate & VIX (FRED)
* [ ] Ticket #5 — Service systemd + Nginx conf
* [ ] Ticket #6 — Android ForegroundService & UI Compose

## 📝 Licence

Projet sous licence **MIT** (voir fichier `LICENSE`).
