# 📱 GoldMarket Live — Application Android avec Notification Économique Temps Réel (USA)

> **Statut** : 🚧 En développement  
> **Backend** : FastAPI (Python 3.10+)  
> **Frontend** : Android natif (Kotlin, Jetpack Compose)  
> **OS Cible** : Android 8.0+ (.apk installable manuellement)  
> **Déploiement** : VPS Debian 12 (OVH), systemd + Nginx

---

## 🎯 Objectif

Afficher dans une **notification permanente dynamique** sur Android, en temps réel :

- 🔺 **Taux actuel de la FED**
- 🗓️ **Prochaine réunion FOMC**
- 🎤 **Prochain discours de Powell**
- 📊 **Dernière statistique macro US** (CPI, NFP ou PCE)
- 📉 **DXY (via UUP)**
- 😱 **VIX (volatilité US, via FRED)**
- 💰 **Volume global du marché US** (NYSE + Nasdaq, via SPY + QQQ)

Toutes les données proviennent de **sources officielles gratuites**, sans scraping : FRED, BLS, BEA, Alpha Vantage, RSS Fed.

---

## 🏗️ Architecture

### Backend : `FastAPI` + `cachetools`

- Centralise et normalise toutes les données économiques.
- Expose des endpoints REST unifiés.
- Implémente un cache TTL par source pour respecter les quotas.
- Déployé sur **Debian 12** avec **Gunicorn + systemd + Nginx**.

### Frontend : `Kotlin` + `Jetpack Compose`

- UI minimale (liste d'indicateurs)
- ForegroundService résilient pour maintenir la notification à l’écran
- Rafraîchissement silencieux toutes les 30s
- Communication via Retrofit vers API REST interne

---

## 🔌 Endpoints REST disponibles

| Endpoint | Donnée retournée |
|---------|------------------|
| `/api/v1/fed_rate` | Taux actuel de la FED |
| `/api/v1/fomc_next` | Date de la prochaine réunion FOMC |
| `/api/v1/powell_speech` | Détail du prochain discours de Powell |
| `/api/v1/latest_macro` | Dernière statistique macro publiée (CPI/NFP/PCE) |
| `/api/v1/market_indices` | Indice DXY (proxy UUP) + VIX |
| `/api/v1/us_market_volume` | Volume global (SPY + QQQ) |

---

## ⚙️ Technologies

### Backend

- Python 3.10+
- FastAPI
- cachetools
- requests, feedparser
- Gunicorn / systemd
- Nginx (reverse proxy)

### Android

- Kotlin
- Jetpack Compose
- Retrofit
- ForegroundService (type: `dataSync`)
- CoroutineScope pour boucle de mise à jour

---

## 🛡️ Sécurité & Bonnes pratiques

- Aucun scraping, que des APIs **officielles**.
- Backend en lecture seule, sans persistence.
- .env avec variables API : `FRED_API_KEY`, `BEA_API_KEY`, `ALPHA_API_KEY`, etc.
- Signature d’APK en release via `keytool`.

---

## 🧠 Cache TTL (backend)

| Donnée | TTL |
|--------|-----|
| FE
