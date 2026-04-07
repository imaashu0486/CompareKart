# CompareKart

Last updated: 2026-04-08

CompareKart is a smartphone price comparison platform focused on Indian e-commerce marketplaces.
It combines a FastAPI backend, MongoDB-backed product APIs, and a React Native (Expo) mobile app.

The goal is straightforward: fetch marketplace prices, clean noisy values, and present a dependable compare experience.

---

## 1. What this project does

- Aggregates smartphone pricing from Amazon, Flipkart, and Croma
- Computes `best_price` and `best_platform` per product
- Supports side-by-side comparison (up to 4 products)
- Provides retry controls for incomplete data:
	- full product retry
	- single-platform retry
- Normalizes product naming so UI titles stay clear (`Brand + Model`)

---

## 2. High-level architecture

### Backend

- Framework: FastAPI
- Main entry: `backend/main.py`
- Active routes:
	- `backend/routes/mobile_auth_routes.py`
	- `backend/routes/mobile_product_routes.py`
- Data layer: MongoDB via `backend/mongo_db.py`
- Scraping and fallback orchestration:
	- `backend/services/amazon_service.py`
	- `backend/services/flipkart_service.py`
	- `backend/services/croma_service.py`
	- `backend/mongo_scraper.py`
- Selenium guard and fallback control:
	- `backend/utils/selenium_driver.py`

### Frontend

- Framework: React Native + Expo
- Main app: `frontend/smart_comparator_app`
- App shell: `frontend/smart_comparator_app/App.js`
- Navigation: `frontend/smart_comparator_app/src/navigation/RootNavigator.js`
- Auth state: `frontend/smart_comparator_app/src/context/AuthContext.js`
- Product/app state: `frontend/smart_comparator_app/src/store/AppStore.js`
- API client: `frontend/smart_comparator_app/src/services/api.js`

### Secondary workspace in repo

- Flutter app exists in `frontend/comparekart_app`
- Active mobile flow is the React Native app above

---

## 3. Backend lifecycle and runtime behavior

When the API server starts:

1. Environment variables are loaded.
2. SQL init path runs for compatibility.
3. Mongo indexes are initialized.
4. Product and auth routers are mounted.

When the server stops:

- Mongo client is closed cleanly.

Health and docs:

- `GET /health`
- Swagger docs at `/docs`

---

## 4. Data model (practical view)

Typical product fields include:

- `category`, `brand`, `model`, `variant_name`
- `amazon_url`, `flipkart_url`, `croma_url`
- `prices`: `{ amazon, flipkart, croma }`
- `best_price`, `best_platform`
- `image_url`, `specifications`, `last_updated`

Before response output, prices are sanitized and best-price selection is recomputed.

---

## 5. Price quality controls

The API filters out bad values before sending data to the app.

Key logic:

- Invalid numeric values are dropped
- Non-positive values are dropped
- For phone categories, very low values (offer/EMI artifacts) are blocked
- `best_price` is selected only from valid platform prices

This is why obviously wrong values do not appear in compare cards.

---

## 6. Scraping pipeline and fallback strategy

Price refresh follows a layered strategy:

1. Direct platform scrape from product URLs
2. If data is missing, query-based fallback per platform
3. Selenium fallback only when needed
4. Merge + sanitize + update document

Reliability protections:

- per-platform timeout
- per-product timeout
- cache freshness checks
- guarded Selenium behavior for repeated failures

---

## 7. Auth flow

Backend auth endpoints:

- `POST /auth/signup`
- `POST /auth/login`
- `GET /auth/me`

Auth implementation details:

- password hashing with PBKDF2
- JWT bearer tokens (`HS256`)
- token persisted on device in AsyncStorage
- app restores session on launch and hydrates user profile

---

## 8. Product refresh and retry endpoints

Core endpoints:

- `GET /products`
- `GET /product/{product_id}`
- `POST /product/{product_id}/retry-prices`
- `POST /product/{product_id}/retry-platform/{platform}` where `platform` is `amazon`, `flipkart`, or `croma`
- `POST /update-prices`
- `POST /update-prices-quick`

Why retries exist:

- marketplace pages are dynamic
- one platform can fail while others succeed
- targeted retries reduce unnecessary scraping load

---

## 9. Frontend behavior and state

The app keeps two main state layers:

1. Auth/session state (`AuthContext`)
2. Product + compare + wishlist state (`AppStore`)

Key UX behavior:

- compare list capped at 4 products
- wishlist and recent searches persisted
- compare and details screens consume normalized product data
- retry actions are accessible from product detail views

---

## 10. API base URL resolution (Expo)

The app resolves backend URL in this order:

1. `EXPO_PUBLIC_API_BASE_URL`
2. host information from Expo runtime
3. fallback defaults:
	 - Android emulator: `http://10.0.2.2:8000`
	 - iOS/local: `http://localhost:8000`

This avoids hardcoded machine-specific addresses in most cases.

---

## 11. Local development

### Backend

1. Create/activate virtual environment
2. Install dependencies from `backend/requirements.txt`
3. Start server from `backend`:
	 - `uvicorn main:app --host 0.0.0.0 --port 8000`
4. Check `http://localhost:8000/health`

### React Native app

1. Go to `frontend/smart_comparator_app`
2. Install dependencies (`npm install`)
3. Start Expo (`npx expo start`)
4. Run on emulator/device

---

## 12. Repository notes

- Active production-like path is Mongo + mobile routes + React Native app
- Legacy SQL-era files are retained for compatibility/history
- Flutter workspace remains in repo as secondary implementation

---

## 13. Quick troubleshooting

### Backend not reachable

- verify venv activation and dependency installation
- confirm port 8000 is free
- check startup logs for import/env errors

### App cannot call API on emulator

- confirm backend health works from host
- verify resolved base URL behavior
- on Android emulator, use `10.0.2.2`

### Missing price on one platform

- run platform retry endpoint first
- then run full retry if still incomplete
- confirm product has that platform URL saved

---

## 14. Useful URLs

- API health: [http://localhost:8000/health](http://localhost:8000/health)
- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 14.1 Live links

- Live backend base URL: [https://comparekart-puc5.onrender.com](https://comparekart-puc5.onrender.com)
- Live backend health: [https://comparekart-puc5.onrender.com/health](https://comparekart-puc5.onrender.com/health)
- Latest Android build page: [https://expo.dev/accounts/imaashu0486/projects/comparekart/builds/19093902-e954-411f-ac8f-d2867edcc42b](https://expo.dev/accounts/imaashu0486/projects/comparekart/builds/19093902-e954-411f-ac8f-d2867edcc42b)
- Latest Android APK direct download: [https://expo.dev/artifacts/eas/46iZwzzBS8h2us8rRrvnhx.apk](https://expo.dev/artifacts/eas/46iZwzzBS8h2us8rRrvnhx.apk)

Note: direct artifact links can rotate/expire; if a link fails, open the latest build page and download the newest artifact.

---

## 15. Deploy online (backend + database + APK)

### A) Online database (MongoDB Atlas)

1. Create a MongoDB Atlas cluster.
2. Create database user + password.
3. Add IP access (or `0.0.0.0/0` for initial setup).
4. Copy connection string as `MONGO_URI`.

### B) Backend always running (Render)

This repo includes:

- [render.yaml](render.yaml)
- [backend/Dockerfile](backend/Dockerfile)

Deploy steps:

1. Push code to GitHub.
2. In Render, create service from repo (Blueprint or Web Service).
3. Set env vars in Render:
	- `MONGO_URI` = Atlas connection string
	- `MONGO_DB_NAME` = `smart_price_comparator` (or your value)
	- `JWT_SECRET` = strong random secret
	- `JWT_EXPIRE_MINUTES` = `10080`
4. Deploy and verify:
	- [https://your-backend-domain/health](https://your-backend-domain/health)

### C) Android APK (Expo EAS)

This repo includes:

- [frontend/smart_comparator_app/eas.json](frontend/smart_comparator_app/eas.json)

Before build:

1. Replace `https://YOUR_BACKEND_DOMAIN` in `eas.json` with deployed backend URL.
2. Install and login:
	- `npm install -g eas-cli`
	- `eas login`

Build APK:

1. Go to `frontend/smart_comparator_app`
2. Run `eas build -p android --profile preview`
3. Download APK from EAS build URL and install on mobile.

For Play Store later:

- Run `eas build -p android --profile production` to create AAB.

---

## 16. Future improvements (rolling roadmap)

This project will be improved continuously. The items below are active next-step targets.

### Product data and quality

- Broaden catalog coverage beyond smartphones (laptops, tablets, accessories)
- Improve variant normalization to reduce duplicate-looking products
- Add stronger image/spec fallback rules for partially scraped products
- Add confidence scoring for scraped price quality

### Scraping reliability

- Add smarter retry scheduling with exponential backoff per platform
- Add better anti-block handling and dynamic selector recovery
- Add platform health metrics and automatic temporary disable on repeated failures
- Add periodic refresh jobs with configurable priority queues

### Backend and APIs

- Add pagination and sorting controls for `/products`
- Add richer filters (RAM, storage, chipset, brand families)
- Add cache layer for hot endpoints to reduce latency
- Add structured audit logs for refresh/retry workflows

### Mobile app UX

- Add saved compare presets and price-drop watchlists
- Add push notifications for significant price changes
- Add improved offline handling and cached last-seen results
- Add deeper product insights view (price history, trend signals)

### Ops and delivery

- Add CI checks for backend + app smoke tests on every push
- Add scheduled backup/restore validation for MongoDB
- Add release notes automation for each APK build
- Add environment health dashboard for backend, DB, and scraper pipelines

### Security and governance

- Rotate secrets regularly and move all secrets to managed secret stores
- Add stricter auth monitoring and suspicious activity alerts
- Add role-based admin endpoints for operational actions

This roadmap is intentionally iterative and will evolve with each release.




