# CompareKart

CompareKart is a production-oriented mobile price comparison platform for smartphones in India.  
The system aggregates marketplace pricing, normalizes product records, and provides user-facing comparison workflows with resilient retry and refresh controls.

## Project Scope

CompareKart delivers:

- Multi-platform phone price aggregation (Amazon, Flipkart, Croma)
- Best-price and best-platform selection per product
- Product details with per-platform retry and full retry actions
- Side-by-side comparison for up to 4 products
- Data-quality safeguards against unrealistic price artifacts
- Operational refresh endpoints for bulk and targeted updates

## Data Acquisition Strategy (Evolution)

The project evolved through three stages:

1. **Direct marketplace scraping** (requests + BeautifulSoup)
2. **Search-API experimentation** (Google/SerpAPI exploration during refinement)
3. **Current stable pipeline**:
	 - Direct URL scraping as primary path
	 - Query-based fallback when platform data is missing
	 - Controlled Selenium fallback for difficult pages
	 - Selenium guardrail (temporary disable on repeated session failures)

This keeps reliability high while preserving data coverage.

## System Architecture

### Backend (FastAPI)

- API framework: FastAPI
- Core routes: product, auth, mobile product/auth routes
- Scraper services: Amazon, Flipkart, Croma
- Resilience controls:
	- per-product and per-platform timeouts
	- fallback enrichment on missing platform prices
	- per-product and per-platform retry endpoints
	- minimum valid phone price threshold filtering

### Frontend (React Native, Expo)

- Main client: `frontend/smart_comparator_app`
- Key UX: browse, wishlist, compare, product details, retry actions
- Compare and detail views consume normalized backend product responses

### Secondary client workspace

- `frontend/comparekart_app` (Flutter workspace kept in repository)

## Database Setup (Local vs Production)

**Current default is local database usage.**

- Primary active data path (mobile routes): **MongoDB local instance**
	- default URI: `mongodb://localhost:27017`
	- configured in backend mongo DB layer using environment fallback
- Legacy SQL artifacts also exist in repository (SQLite-oriented modules and `.db` files) for earlier flow compatibility.

For your current working mobile flow, MongoDB local is the primary source.

## Important API Endpoints

- `GET /health`
- `GET /products`
- `GET /product/{product_id}`
- `POST /product/{product_id}/retry-prices`
- `POST /product/{product_id}/retry-platform/{platform}` where platform is `amazon|flipkart|croma`
- `POST /update-prices`
- `POST /update-prices-quick`

## Local Run

### Backend

1. Create and activate Python virtual environment
2. Install backend dependencies
3. Start API on port 8000
4. Verify `GET /health` returns 200

### Mobile app

1. Go to `frontend/smart_comparator_app`
2. Install dependencies
3. Start Expo
4. Run on emulator/device

## Submission Readiness Notes

- Repository markdown clutter was consolidated to this single README.
- Root `.gitignore` is configured for virtual environments, build outputs, caches, logs, local DB files, and artifacts.
- Project is initialized for git with main branch, ready for commit and push.
