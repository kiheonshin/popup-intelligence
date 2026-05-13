# popup-intelligence

성수동 팝업 스토어 인터랙티브 분석 (2015–2025) · Idola 디자인 시스템 적용

> **Live demo** → https://kiheonshin.github.io/popup-intelligence/

2015–2025년 사이 성수동 일대에서 운영된 **2,729개 팝업 스토어 / 1,866개 고유 브랜드**를 50개 AI 에이전트 병렬 수집으로 통합한 데이터셋을 인터랙티브 웹페이지로 시각화합니다.

## 메뉴

| 메뉴 | 설명 |
| --- | --- |
| **📊 대시보드** | 연도·카테고리·국적·구역·브랜드 필터로 차트와 테이블을 실시간 갱신 |
| **📖 스토리** | 6개 챕터 (태동기→폭발→탈성수)의 스크롤 내러티브, 우측 차트 자동 하이라이트 |
| **🗺️ 지도** | Leaflet 다크 타일 위 구역별 원형 마커 (log 스케일), 카테고리 필터 |
| **💸 상권 영향** | 임대료·외국인 방문객·폐업·경제 가치의 11년 곡선 + 핵심 인사이트 |

## 디자인

[Idola Design System](https://) 기반의 다크 HUD 룩:

- 배경 `#0c1016`, 액센트 시그니처 **라임 `#c2ff77`**
- 타이포: IBM Plex Mono (라벨/숫자) + IBM Plex Sans KR (본문) + Space Grotesk (디스플레이)
- "Operator console for an emergent world" 컨셉을 도시 데이터 시각화에 적용

## 구조

```
popup-intelligence/
├── index.html              # 단일 파일 SPA (Plotly + Leaflet, 데이터 inline)
├── docs/
│   ├── build_data.py       # CSV → 집계 JSON 빌드 스크립트
│   ├── data.json           # 집계 결과 (사람이 읽기 좋은 형식)
│   ├── data.min.json       # 집계 결과 (minified, index.html에 임베드된 것과 동일)
│   └── source_data/        # 원본 데이터
│       ├── 성수동_팝업스토어_통합DB_2015_2025.csv  (2,729건)
│       ├── 성수동_팝업스토어_통합DB_2015_2025.json
│       ├── popup_meta_economy.json
│       ├── 성수동_팝업스토어_분석보고서_2015_2025.md
│       ├── seongsu_district_trend_report.md
│       └── popup_economy_report.md
└── README.md
```

## 로컬 실행

```sh
python3 -m http.server 8765
# → http://localhost:8765/
```

또는 단일 파일이므로 `index.html` 을 더블클릭으로 열어도 동작합니다 (CDN으로 Plotly·Leaflet·IBM Plex 로드).

## 데이터 재빌드

원본 CSV에서 집계를 다시 만들고 싶다면:

```sh
python3 docs/build_data.py
```

CSV 컬럼: `ID, 브랜드명, 팝업스토어명, 카테고리, 세부카테고리, 시작일, 종료일, 운영일수, 위치, 구역, 원산지(원본), 원산지(정제), 콜라보, 설명, 연도, 출처`

## 핵심 인사이트

- **2022년 임계점**: 팝업 수 +113%로 100건 돌파 → 메가 상권 진입
- **2024년 정점**: 560건, 외국인 방문 300만 명 (2018 대비 ×50)
- **2025년 전환**: 662건으로 사상 최대지만 임대료 폭등으로 *탈성수* 현상 시작 (팝업 트렌드 유통사 쇼핑몰 43% 추월)
- **경제적 가치**: 4,364억(2014) → 1조5,497억(2024), +255%
- **그늘**: 폐업 86→180건 (4년 연속 증가), 임대료 5년간 +48% (서울 평균의 3배)

## 라이선스

데이터 출처는 각 보고서 본문 참고. 시각화 코드는 자유롭게 사용 가능.
