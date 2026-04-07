# CompareKart

CompareKart is a mobile-first smartphone price comparison platform built for Indian e-commerce marketplaces. It collects product pricing, applies quality filters, and delivers a reliable compare experience through a resilient backend pipeline and production-oriented mobile UI.

---

## 1) Project Overview

### Primary objective
Help users quickly identify the best available smartphone price across major platforms.

### Core capabilities
- Marketplace aggregation across **Amazon**, **Flipkart**, and **Croma**
- Best-price and best-platform selection per product
- Side-by-side comparison (up to 4 devices)
- Product detail enrichment with **full retry** and **platform retry** actions
- Data quality safeguards (invalid low-price suppression, fallback enrichment)

---

## 2) Data Acquisition Journey

The data strategy evolved in phases:

1. **Direct marketplace scraping** using requests + HTML parsing
2. **Search API experimentation** (Google/SerpAPI exploration during refinement)
3. **Current production flow**:
	 - direct URL scrape as primary path
	 - query-based fallback when direct scrape is incomplete
	 - Selenium fallback only when necessary
	 - Selenium circuit-breaker behavior on repeated session instability

This approach balances coverage, speed, and operational stability.

---

## 3) Architecture

### Backend
- Framework: **FastAPI**
- Key modules:
	- `backend/routes/mobile_product_routes.py`
	- `backend/services/*` (platform scrapers)
	- `backend/mongo_scraper.py` (aggregation/scrape orchestration helpers)
	- `backend/utils/selenium_driver.py` (guarded Selenium lifecycle)
- Reliability features:
	- per-platform + per-product timeouts
	- selective fallback enrichment for missing platform values
	- retry endpoints (`retry-prices`, `retry-platform`)
	- minimum valid phone price filtering

### Frontend
- Framework: **React Native (Expo)**
- Primary app: `frontend/smart_comparator_app`
- UX highlights:
	- premium browse and compare UI
	- clean product naming (`Brand + Model` as primary)
	- retry controls from product details
	- stateful wishlist and compare flows

### Secondary workspace
- `frontend/comparekart_app` (Flutter workspace retained in repo)

---

## 4) Database Clarification (Local vs Production)

Yes — for the current mobile product flow, the active default is **local MongoDB**.

- Default Mongo URI fallback: `mongodb://localhost:27017`
- Implemented in Mongo DB access layer (`backend/mongo_db.py`)

Legacy SQL/SQLite scaffolding is still present for earlier compatibility paths, but the live mobile routes are backed by MongoDB.

---

## 5) API Surface (Key Endpoints)

- `GET /health`
- `GET /products`
- `GET /product/{product_id}`
- `POST /product/{product_id}/retry-prices`
- `POST /product/{product_id}/retry-platform/{platform}` where `platform ∈ {amazon, flipkart, croma}`
- `POST /update-prices`
- `POST /update-prices-quick`

---

## 6) Local Development

### Backend
1. Create and activate Python virtual environment
2. Install dependencies from `backend/requirements.txt`
3. Start backend on port 8000
4. Verify health endpoint returns 200

### Mobile App (React Native)
1. Open `frontend/smart_comparator_app`
2. Install dependencies
3. Start Expo dev server
4. Launch on emulator or physical device

---

## 7) Quality and Reliability Notes

- API responses are sanitized before being exposed to client UI
- Missing platform prices can be enriched on-demand
- Retry actions are available at both product and platform granularity
- Selenium fallback is guarded to reduce cascading failures from unstable sessions

---

## 8) Submission Readiness

- Documentation consolidated into this single root README
- Root `.gitignore` configured to exclude environments, build outputs, logs, artifacts, and local data files
- Repository initialized and structured for clean git push

