#!/usr/bin/env python3
"""Aggregate the Seongsu pop-up CSV + meta JSONs into one stats JSON for the web page."""
import csv, json, collections, re, os
from pathlib import Path

ROOT = Path("/Users/artifact/Claude/projects/Sweet Spot/Kimi_Agent_성수동 팝업스토어 분석")
OUT = Path("/Users/artifact/Claude/projects/Sweet Spot/web/data.json")

CSV_PATH = ROOT / "성수동_팝업스토어_통합DB_2015_2025.csv"

# ---------- normalizers ----------
def norm_category(raw: str) -> str:
    if not raw: return "기타"
    s = raw.strip().lower()
    if s in ("", "n/a", "기타"): return "기타"
    # English -> Korean canonical
    if s.startswith("beauty"): return "뷰티"
    if s.startswith("fashion"): return "패션"
    if s.startswith("food") or s.startswith("f&b") or s.startswith("fb"): return "F&B"
    if s.startswith("tech"): return "테크"
    if s.startswith("art"): return "예술"
    if s.startswith("ent"): return "엔터테인먼트"
    if s.startswith("sport"): return "스포츠"
    if s.startswith("life"): return "라이프스타일"
    if s.startswith("char") or "ip" in s: return "캐릭터/IP"
    if s.startswith("auto") or s.startswith("car"): return "자동차"

    r = raw.strip()
    # Korean rules — keep prefix before "/"
    head = r.split("/")[0].strip()
    mapping = {
        "패션": "패션", "패션의류": "패션",
        "뷰티": "뷰티", "뷰티향수": "뷰티",
        "F&B": "F&B", "식음료": "F&B", "F&B/주류": "F&B", "주류": "F&B",
        "라이프스타일": "라이프스타일", "리빙": "라이프스타일",
        "예술": "예술", "아트": "예술", "전시": "예술",
        "엔터": "엔터테인먼트", "엔터테인먼트": "엔터테인먼트",
        "스포츠": "스포츠",
        "테크": "테크", "전자기기": "테크", "IT": "테크",
        "자동차": "자동차",
        "캐릭터": "캐릭터/IP", "굿즈": "캐릭터/IP", "IP": "캐릭터/IP",
        "K-POP": "엔터테인먼트", "K팝": "엔터테인먼트", "아이돌": "엔터테인먼트",
    }
    if head in mapping: return mapping[head]
    # Fallback partial
    for k, v in mapping.items():
        if k in head: return v
    return "기타"

def norm_origin(raw: str) -> str:
    if not raw: return "불명"
    s = raw.strip()
    if s in ("국내", "Korea", "한국", "대한민국") or s.startswith("한국(") or s.startswith("Korea ") or s.startswith("국내"):
        return "국내"
    if "/" in s or "X" in s or "콜라보" in s:
        return "콜라보"
    if s in ("불명", "N/A", "복합"): return "불명"
    if s in ("미국",) or "미국" in s and "한국" not in s: return "미국"
    if s in ("프랑스",) or "프랑스" in s: return "프랑스"
    if s in ("일본",) or "일본" in s: return "일본"
    if s in ("영국",) or "영국" in s: return "영국"
    if s in ("독일",) or "독일" in s: return "독일"
    if s in ("이탈리아", "Italy") or "이탈리아" in s: return "이탈리아"
    if s in ("중국",) or "중국" in s: return "중국"
    if s.startswith("Global") or "글로벌" in s: return "기타 해외"
    return "기타 해외"

def norm_district(raw: str, location: str) -> str:
    """Map to canonical district. Try district col first, then location text."""
    src = (raw or "").strip()
    loc = (location or "").strip()
    blob = (src + " " + loc).lower()
    # priority order matters — more specific first
    if "연무장" in blob: return "연무장길"
    if "서울숲" in blob: return "서울숲"
    if "뚝섬" in blob: return "뚝섬"
    if "대림창고" in blob: return "대림창고/복합문화"
    if "성수 복합문화" in blob or "복합문화" in blob: return "대림창고/복합문화"
    if "성수 아트" in blob or "아트" in blob and "성수" in blob: return "성수 아트/문화"
    if "성수1가" in blob or "성수일가" in blob or "성수 1가" in blob: return "성수1가"
    if "성수2가" in blob or "성수이가" in blob or "성수 2가" in blob: return "성수2가"
    if "왕십리" in blob or "행당" in blob: return "왕십리/행당"
    if "성수이로" in blob: return "성수이로"
    if "성수" in blob: return "성수 기타"
    return "미상"

def parse_year(row):
    y = (row.get("연도") or "").strip()
    if y.isdigit(): return int(y)
    s = (row.get("시작일") or "")
    m = re.match(r"(\d{4})", s)
    return int(m.group(1)) if m else None

from datetime import datetime
def compute_duration(row):
    raw = (row.get("운영일수") or "").strip()
    if raw.isdigit(): return int(raw)
    s, e = (row.get("시작일") or "").strip(), (row.get("종료일") or "").strip()
    for fmt in ("%Y-%m-%d", "%Y.%m.%d", "%Y/%m/%d"):
        try:
            sd, ed = datetime.strptime(s, fmt), datetime.strptime(e, fmt)
            n = (ed - sd).days + 1
            return n if 0 < n < 1000 else None
        except Exception:
            continue
    return None

# ---------- aggregate ----------
rows = list(csv.DictReader(open(CSV_PATH, encoding="utf-8-sig")))

popups = []
for row in rows:
    year = parse_year(row)
    cat = norm_category(row.get("카테고리", ""))
    origin = norm_origin(row.get("원산지(정제)", "") or row.get("원산지(원본)", ""))
    district = norm_district(row.get("구역", ""), row.get("위치", ""))
    popups.append({
        "id": row.get("ID"),
        "brand": row.get("브랜드명", "").strip(),
        "name": row.get("팝업스토어명", "").strip(),
        "category": cat,
        "subcategory": row.get("세부카테고리", "").strip(),
        "start": row.get("시작일", "").strip(),
        "end": row.get("종료일", "").strip(),
        "duration": compute_duration(row),
        "location": row.get("위치", "").strip(),
        "district": district,
        "origin": origin,
        "collab": row.get("콜라보", "").strip(),
        "description": (row.get("설명", "") or "")[:240],
        "year": year,
    })

# Aggregations
by_year = collections.Counter(p["year"] for p in popups if p["year"])
by_year_origin_kr = collections.Counter((p["year"], p["origin"] == "국내") for p in popups if p["year"])
by_cat = collections.Counter(p["category"] for p in popups)
by_origin = collections.Counter(p["origin"] for p in popups)
by_district = collections.Counter(p["district"] for p in popups)
by_year_cat = collections.defaultdict(lambda: collections.Counter())
for p in popups:
    if p["year"]:
        by_year_cat[p["year"]][p["category"]] += 1

# Top brands (excluding empty)
brand_counter = collections.Counter(p["brand"] for p in popups if p["brand"])

# Duration buckets
def duration_bucket(p):
    n = p["duration"]
    if not isinstance(n, int) or n <= 0: return None
    if n <= 3: return "≤3일 (초단기)"
    if n <= 7: return "4-7일 (일주일)"
    if n <= 14: return "8-14일 (2주)"
    if n <= 30: return "15-30일 (한 달)"
    if n <= 90: return "31-90일 (분기)"
    return "90일+"
duration_dist = collections.Counter(filter(None, (duration_bucket(p) for p in popups)))

# ---------- load meta_economy for timeline ----------
meta_econ_path = ROOT / "popup_meta_economy.json"
econ = json.load(open(meta_econ_path, encoding="utf-8"))

# Extract a clean yearly timeline
timeline = []
for y in econ.get("yearly_data", []):
    timeline.append({
        "year": y.get("year"),
        "rent": y.get("avg_rent_per_sqm"),
        "rent_change": y.get("rent_change_rate"),
        "businesses": y.get("business_count"),
        "revenue_trillion": y.get("business_revenue_trillion"),
        "visitor_domestic_M": y.get("visitor_domestic_million"),
        "visitor_foreign": y.get("visitor_foreign"),
        "popup_count": y.get("popup_count"),
        "closed_stores": y.get("closed_stores"),
        "vacancy_rate": y.get("vacancy_rate"),
        "economic_value_billion": y.get("economic_value_billion"),
        "workers": y.get("workers_count"),
        "key_changes": y.get("key_changes", []),
    })

# ---------- District meta with approximate coords ----------
# Hand-curated lat/lng for Seongsu sub-districts (rough centroids)
district_geo = {
    "연무장길":       {"lat": 37.5443, "lng": 127.0561, "blurb": "팝업의 절대 중심지. 명품·디자이너 브랜드 집결."},
    "서울숲":         {"lat": 37.5443, "lng": 127.0379, "blurb": "감성 팝업·자연 연계. 아모레성수, 정원박람회."},
    "뚝섬":           {"lat": 37.5470, "lng": 127.0470, "blurb": "대형 팝업·한강 연계. 갤럭시스튜디오, 넷플릭스."},
    "성수1가":        {"lat": 37.5446, "lng": 127.0463, "blurb": "성수역 북단. 카페·갤러리 상권."},
    "성수2가":        {"lat": 37.5470, "lng": 127.0568, "blurb": "수제화 거리 + 신흥 팝업. 임대료 급등 핵심지."},
    "대림창고/복합문화": {"lat": 37.5440, "lng": 127.0540, "blurb": "공장→문화공간 전유 시작점. 인프라 원조."},
    "성수 아트/문화": {"lat": 37.5435, "lng": 127.0500, "blurb": "전시·예술 팝업 중심."},
    "성수이로":       {"lat": 37.5455, "lng": 127.0530, "blurb": "무신사·LCDC·에스팩토리 라인."},
    "왕십리/행당":     {"lat": 37.5613, "lng": 127.0379, "blurb": "성수 연계 인접 상권."},
    "성수 기타":      {"lat": 37.5450, "lng": 127.0550, "blurb": "기타 성수 구역."},
    "미상":           None,
}

district_stats = []
for name, count in by_district.most_common():
    geo = district_geo.get(name)
    if not geo: continue
    district_stats.append({
        "name": name,
        "count": count,
        "lat": geo["lat"],
        "lng": geo["lng"],
        "blurb": geo["blurb"],
    })

# ---------- build outputs ----------
out = {
    "totals": {
        "popups": len(popups),
        "brands": len(brand_counter),
        "years_covered": "2015-2025",
    },
    "by_year": [{"year": y, "count": by_year[y]} for y in sorted(by_year)],
    "by_year_cat": [
        {"year": y, **{c: by_year_cat[y].get(c, 0) for c in [
            "패션","뷰티","F&B","라이프스타일","예술","엔터테인먼트","스포츠","테크","자동차","캐릭터/IP","기타"
        ]}}
        for y in sorted(by_year_cat)
    ],
    "by_category": [{"name": c, "count": n} for c, n in by_cat.most_common()],
    "by_origin": [{"name": o, "count": n} for o, n in by_origin.most_common()],
    "by_district": district_stats,
    "duration_dist": [
        {"bucket": b, "count": duration_dist[b]}
        for b in ["≤3일 (초단기)","4-7일 (일주일)","8-14일 (2주)","15-30일 (한 달)","31-90일 (분기)","90일+"]
        if duration_dist[b]
    ],
    "top_brands": [{"brand": b, "count": n} for b, n in brand_counter.most_common(30)],
    "timeline": timeline,
    "popups": popups,
}

OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"Wrote {OUT} ({OUT.stat().st_size / 1024:.1f} KB)")
print("totals:", out["totals"])
print("by_year sample:", out["by_year"][:3], "...", out["by_year"][-2:])
print("category count:", len(out["by_category"]))
print("districts:", [(d["name"], d["count"]) for d in out["by_district"]])
print("durations:", out["duration_dist"])
print("timeline rows:", len(out["timeline"]))
