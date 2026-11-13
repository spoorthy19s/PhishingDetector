from urllib.parse import urlparse
import math, re, tldextract

SUSPICIOUS_TLDS = {"top", "xyz", "tk", "ml", "ga", "cf", "gq", "click", "zip"}
KEYWORDS = ("login", "verify", "secure", "account", "update", "bank", "confirm")

def entropy(s):
    if not s: return 0.0
    p = [s.count(c) / len(s) for c in set(s)]
    return -sum(x * math.log2(x) for x in p)

def extract(url: str) -> dict:
    u = url.strip()
    parsed = urlparse(u if "://" in u else "http://" + u)
    ext = tldextract.extract(u)
    host = parsed.netloc.split("@")[-1]
    return {
        "is_https": int(parsed.scheme == "https"),
        "has_at": int("@" in parsed.netloc),
        "is_ip_host": int(bool(re.fullmatch(r"[\d.]+", ext.domain + "." + ext.suffix) or re.fullmatch(r"\d+\.\d+\.\d+\.\d+", host.split(":")[0]))),
        "subdomain_depth": len([s for s in ext.subdomain.split(".") if s]),
        "tld_suspicious": int(ext.suffix.split(".")[-1] in SUSPICIOUS_TLDS),
        "domain_len": len(ext.domain),
        "domain_hyphens": ext.domain.count("-"),
        "domain_digit_ratio": sum(c.isdigit() for c in ext.domain) / max(1, len(ext.domain)),
        "domain_entropy": entropy(ext.domain),
        "path_len": len(parsed.path),
        "n_params": len([p for p in parsed.query.split("&") if p]),
        "kw_in_domain": int(any(k in (ext.subdomain + ext.domain).lower() for k in KEYWORDS)),
        "kw_in_path": int(any(k in parsed.path.lower() for k in KEYWORDS)),
        "url_len": len(u),
    }