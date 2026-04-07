"""
Utility functions for web scraping.
Includes user agents, headers, retry logic, and common helper functions.
"""

import random
import re
import time
import logging
from typing import Dict, Optional, List
from requests import Response
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from rapidfuzz import fuzz

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Junk keywords to filter out
JUNK_KEYWORDS = [
    "refurbished",
    "restored",
    "renewed",
    "case",
    "cover",
    "screen guard",
    "watch",
    "charger",
    "adapter",
    "bundle",
    "plan",
]


def normalize_title(title: str) -> str:
    """Normalize product title for matching.
    
    Args:
        title: Raw product title
        
    Returns:
        Normalized title
    """
    if not title:
        return ""
    
    # Lowercase
    normalized = title.lower()
    
    # Remove punctuation
    normalized = re.sub(r'[^a-z0-9\s]', ' ', normalized)
    
    # Standardize GB formatting
    normalized = re.sub(r'(\d+)\s*gb', r'\1gb', normalized)
    
    # Remove extra spaces
    normalized = ' '.join(normalized.split())
    
    return normalized


def is_junk_product(title: str) -> bool:
    """Check if product title contains junk keywords.
    
    Args:
        title: Product title to check
        
    Returns:
        True if product is junk, False otherwise
    """
    if not title:
        return True
    
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in JUNK_KEYWORDS)


def is_valid_platform(platform: str) -> bool:
    """Check if platform is in strict whitelist (FINAL REFINEMENT).
    
    ONLY allow major Indian e-commerce platforms.
    Reject small sellers, resellers, and all non-whitelisted platforms.
    
    Args:
        platform: Seller platform name/URL
        
    Returns:
        True if platform is whitelisted, False otherwise
    """
    if not platform:
        return False
    
    platform_lower = platform.lower().strip()
    
    # STRICT WHITELIST - Only major Indian e-commerce platforms
    whitelist = [
        "amazon.in",
        "amazon",
        "flipkart",
        "croma",
        "reliance digital",
        "reliancedigital",
        "vijay sales",
        "vijaysales",
        "tata cliq",
        "tatacliq",
    ]
    
    # Check if platform matches whitelist
    for allowed in whitelist:
        if allowed in platform_lower:
            return True
    
    return False


def is_new_condition(title: str) -> bool:
    """Check if product is in new condition (FINAL REFINEMENT).
    
    Rejects refurbished, used, resale, and non-new listings.
    
    Args:
        title: Product title
        
    Returns:
        True if new, False otherwise
    """
    if not title:
        return True
    
    title_lower = title.lower()
    
    # Reject non-new and resale listings
    non_new_keywords = [
        "used",
        "refurbished",
        "renewed",
        "open box",
        "grade",
        "fair",
        "good condition",
        "budget",
        "restored",
        "sell",
        "exchange",
        "buyback",
        "pre-owned",
        "second hand",
    ]
    
    return not any(keyword in title_lower for keyword in non_new_keywords)


def extract_mobile_attributes(title: str) -> dict:
    """Extract mobile attributes from title.
    
    Args:
        title: Product title
        
    Returns:
        Dict with brand, model, storage, condition
    """
    if not title:
        return None
    
    title_lower = title.lower()
    
    # Brand extraction
    brands = {
        "apple": ["iphone"],
        "samsung": ["galaxy", "s23", "s24", "a53", "a54", "a55"],
        "oneplus": ["oneplus", "one plus"],
        "xiaomi": ["xiaomi", "redmi"],
        "poco": ["poco"],
        "motorola": ["moto", "motorola"],
        "nokia": ["nokia"],
        "realme": ["realme"],
        "vivo": ["vivo"],
        "oppo": ["oppo"],
    }
    
    brand = None
    for brand_name, keywords in brands.items():
        if any(kw in title_lower for kw in keywords):
            brand = brand_name
            break
    
    if not brand:
        return None
    
    # Storage extraction
    # Prefer explicit ROM/storage mentions; otherwise use the largest GB value
    # that is not marked as RAM/memory.
    storage_candidates: List[int] = []

    explicit_storage_patterns = [
        r'(\d+)\s?gb\s*(?:rom|storage|internal|inbuilt)',
        r'(?:rom|storage|internal|inbuilt)\s*(\d+)\s?gb',
    ]

    for pattern in explicit_storage_patterns:
        for m in re.finditer(pattern, title_lower):
            try:
                storage_candidates.append(int(m.group(1)))
            except (TypeError, ValueError):
                continue

    if not storage_candidates:
        for m in re.finditer(r'(\d+)\s?gb', title_lower):
            try:
                value = int(m.group(1))
            except (TypeError, ValueError):
                continue

            # Ignore RAM-style mentions like "12GB RAM" / "8GB memory"
            tail = title_lower[m.end(): m.end() + 12]
            if re.match(r'\s*(?:ram|memory)\b', tail):
                continue

            storage_candidates.append(value)

    if not storage_candidates:
        return None

    storage = f"{max(storage_candidates)}gb"
    
    # Model extraction
    model = None
    if brand == "apple":
        # iPhone 14 Pro, iPhone 14 Pro Max, iPhone 15, etc.
        model_match = re.search(
            r'iphone\s*(\d+)\s*(pro\s*max|pro|plus)?',
            title_lower
        )
        if model_match:
            num = model_match.group(1)
            variant = model_match.group(2) or ""
            model = f"iphone {num} {variant}".strip()
    elif brand == "samsung":
        # Galaxy S24, S24 Ultra, S24+, etc. (with or without "Galaxy")
        model_match = re.search(
            r'(?:galaxy\s*)?s\s?(\d+)\s*(ultra|\+|plus|fe)?',
            title_lower
        )
        if model_match:
            num = model_match.group(1)
            variant = model_match.group(2) or ""
            model = f"galaxy s{num} {variant}".strip()
    elif brand == "oneplus":
        model_match = re.search(
            r'(?:oneplus|one\s*plus)\s*(\d+)\s*(t|pro)?',
            title_lower
        )
        if model_match:
            num = model_match.group(1)
            variant = model_match.group(2) or ""
            model = f"oneplus {num} {variant}".strip()
    elif brand == "xiaomi":
        model_match = re.search(
            r'(?:xiaomi|redmi)\s*(?:note\s*)?(\d+)\s*(pro|ultra)?',
            title_lower
        )
        if model_match:
            num = model_match.group(1)
            variant = model_match.group(2) or ""
            prefix = "note" if "note" in title_lower else ""
            model = f"xiaomi {prefix} {num} {variant}".strip()
    elif brand == "motorola":
        model_match = re.search(
            r'moto\s*(?:g|e)\s*(\d+)',
            title_lower
        )
        if model_match:
            series = re.search(r'moto\s*(g|e)', title_lower).group(1)
            num = model_match.group(1)
            model = f"moto {series}{num}"
    elif brand == "realme":
        model_match = re.search(
            r'realme\s*([a-z]*\d+[a-z0-9]*)\s*(pro\s*plus|pro\+|pro|max|plus|ultra)?',
            title_lower
        )
        if model_match:
            num = model_match.group(1)
            variant = model_match.group(2) or ""
            model = f"realme {num} {variant}".strip()
    elif brand == "oppo":
        model_match = re.search(
            r'oppo\s*([a-z]*\d+[a-z0-9]*)\s*(pro\s*plus|pro\+|pro|max|plus|lite|neo)?',
            title_lower,
        )
        if model_match:
            series = model_match.group(1)
            variant = model_match.group(2) or ""
            model = f"oppo {series} {variant}".strip()
    elif brand == "vivo":
        model_match = re.search(
            r'vivo\s*([a-z]*\d+[a-z0-9]*)\s*(pro\s*plus|pro\+|pro|max|plus|ultra)?',
            title_lower,
        )
        if model_match:
            series = model_match.group(1)
            variant = model_match.group(2) or ""
            model = f"vivo {series} {variant}".strip()
    elif brand == "poco":
        model_match = re.search(
            r'poco\s*([a-z]*\d+[a-z0-9]*)\s*(pro\s*plus|pro\+|pro|max|plus|ultra|gt)?',
            title_lower,
        )
        if model_match:
            series = model_match.group(1)
            variant = model_match.group(2) or ""
            model = f"poco {series} {variant}".strip()
    elif brand == "nokia":
        model_match = re.search(
            r'nokia\s*([a-z]*\d+[a-z0-9]*)',
            title_lower,
        )
        if model_match:
            series = model_match.group(1)
            model = f"nokia {series}".strip()
    
    if not model:
        return None
    
    return {
        "brand": brand,
        "model": model.lower(),
        "storage": storage.lower(),
        "condition": "new",
    }


def extract_storage_from_query(query: str) -> Optional[str]:
    """Extract storage capacity from query string (FINAL REFINEMENT).
    
    Args:
        query: Search query string
        
    Returns:
        Storage string like '128gb' or None if not found
    """
    if not query:
        return None
    
    # Match storage pattern: \d+\s?gb
    storage_match = re.search(r'(\d+)\s?gb', query.lower())
    if storage_match:
        return f"{storage_match.group(1)}gb"
    
    return None


def extract_ram_from_query(query: str) -> Optional[str]:
    """Extract RAM capacity from query string if specified (FINAL REFINEMENT).
    
    Args:
        query: Search query string
        
    Returns:
        RAM string like '12gb' or None if not found
    """
    if not query:
        return None
    
    # Match RAM pattern: \d+\s?gb\s?ram
    ram_match = re.search(r'(\d+)\s?gb\s?ram', query.lower())
    if ram_match:
        return f"{ram_match.group(1)}gb"
    
    return None


def storage_matches_exactly(product_title: str, query_storage: str) -> bool:
    """Check if product storage exactly matches query storage (FINAL REFINEMENT).
    
    Rejects combo listings like '256GB/512GB'.
    
    Args:
        product_title: Product title from listing
        query_storage: Expected storage from query (e.g., '128gb')
        
    Returns:
        True if storage matches exactly, False otherwise
    """
    if not product_title or not query_storage:
        return False
    
    product_title_lower = product_title.lower()
    
    # Extract all storage mentions in product
    storage_matches = re.findall(r'(\d+)\s?gb', product_title_lower)
    
    if not storage_matches:
        return False
    
    # If multiple storage values, reject (combo/dual storage listing)
    if len(storage_matches) > 1:
        return False
    
    # Check exact match
    product_storage = f"{storage_matches[0]}gb"
    return product_storage == query_storage


def ram_matches_exactly(product_title: str, query_ram: Optional[str]) -> bool:
    """Check if product RAM exactly matches query RAM if specified (FINAL REFINEMENT).
    
    Args:
        product_title: Product title from listing
        query_ram: Expected RAM from query (e.g., '12gb') or None if not specified
        
    Returns:
        True if RAM matches or RAM not specified, False if mismatch
    """
    # If RAM not specified in query, always accept
    if not query_ram:
        return True
    
    if not product_title:
        return False
    
    product_title_lower = product_title.lower()
    
    # Extract RAM from product title
    ram_match = re.search(r'(\d+)\s?gb\s?(?:ram|memory)', product_title_lower)
    
    if not ram_match:
        return False
    
    product_ram = f"{ram_match.group(1)}gb"
    return product_ram == query_ram


def is_valid_price(price: float) -> bool:
    """Check if price is within realistic range for mobile phones (FINAL REFINEMENT).
    
    Args:
        price: Price in INR
        
    Returns:
        True if price is realistic, False otherwise
    """
    if price is None or price <= 0:
        return False
    
    # Mobile price range: 20,000 to 2,00,000 INR
    min_price = 20000
    max_price = 200000
    
    return min_price <= price <= max_price


# Rotating user agents for realistic requests
USER_AGENTS: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120",
]


def get_headers() -> Dict[str, str]:
    """
    Generate realistic headers with rotating user agent.
    
    Returns:
        Dictionary of HTTP headers suitable for web scraping.
    """
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }


def get_session_with_retries(
    retries: int = 3,
    backoff_factor: float = 0.3,
    status_forcelist: tuple = (500, 502, 503, 504),
) -> requests.Session:
    """
    Create a requests session with retry strategy.
    
    Args:
        retries: Number of retry attempts
        backoff_factor: Backoff factor for retries
        status_forcelist: HTTP status codes to retry on
        
    Returns:
        Configured requests.Session with retry logic
    """
    session: requests.Session = requests.Session()
    
    retry_strategy: Retry = Retry(
        total=retries,
        status_forcelist=status_forcelist,
        allowed_methods=["GET", "POST"],
        backoff_factor=backoff_factor,
    )
    
    adapter: HTTPAdapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session


def fetch_page(
    url: str,
    timeout: int = 10,
    verify: bool = True,
    session: Optional[requests.Session] = None,
) -> Optional[Response]:
    """
    Fetch a web page with error handling and rate limiting.
    
    Args:
        url: URL to fetch
        timeout: Request timeout in seconds
        verify: Whether to verify SSL certificates
        session: Optional requests session (creates new if None)
        
    Returns:
        Response object or None if request fails
    """
    if session is None:
        session = get_session_with_retries()
    
    try:
        # Rate limiting - small delay between requests
        time.sleep(random.uniform(0.5, 1.5))
        
        response: Response = session.get(
            url,
            headers=get_headers(),
            timeout=timeout,
            verify=verify,
        )
        response.raise_for_status()
        return response
    
    except requests.exceptions.Timeout:
        logger.warning(f"Timeout fetching {url}")
        return None
    except requests.exceptions.ConnectionError:
        logger.warning(f"Connection error fetching {url}")
        return None
    except requests.exceptions.HTTPError as e:
        logger.warning(f"HTTP error {e.response.status_code} fetching {url}")
        return None
    except Exception as e:
        logger.error(f"Error fetching {url}: {str(e)}")
        return None


def clean_price(price_text: str) -> Optional[float]:
    """
    Parse and clean price from various formats.
    
    Args:
        price_text: Raw price string (e.g., "$99.99", "₹9,999.00", "€49.99")
        
    Returns:
        Float price value or None if parsing fails
    """
    if not price_text:
        return None
    
    try:
        # Remove currency symbols and whitespace
        cleaned: str = price_text.strip()
        cleaned = cleaned.replace("₹", "").replace("$", "").replace("€", "").replace("£", "")
        cleaned = cleaned.replace(",", "").replace(" ", "")
        
        # Extract numeric value
        price: float = float(cleaned)
        return price if price > 0 else None
    
    except (ValueError, AttributeError):
        logger.warning(f"Failed to parse price: {price_text}")
        return None


def normalize_product_name(name: str) -> str:
    """
    Normalize product name for comparison across platforms.
    
    Args:
        name: Product name to normalize
        
    Returns:
        Normalized product name
    """
    if not name:
        return ""
    
    # Convert to lowercase and strip whitespace
    normalized: str = name.lower().strip()
    
    # Remove extra whitespace
    normalized = " ".join(normalized.split())
    
    return normalized


def calculate_similarity(str1: str, str2: str) -> float:
    """
    Calculate simple string similarity for duplicate detection.
    
    Args:
        str1: First string
        str2: Second string
        
    Returns:
        Similarity score (0.0 to 1.0)
    """
    str1 = normalize_product_name(str1)
    str2 = normalize_product_name(str2)
    
    if str1 == str2:
        return 1.0
    
    # Calculate character-level similarity
    common_chars: int = sum(
        1 for c in str1 if c in str2
    )
    
    max_len: int = max(len(str1), len(str2))
    if max_len == 0:
        return 0.0
    
    return common_chars / max_len
