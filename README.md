# AI 뉴스 검증 Copilot

기사 URL을 입력하면 기사 본문을 추출하고, Gemini API(OpenAI 호환 엔드포인트)를 통해 다음 결과를 제공합니다.

1. 기사 AI 작성 가능성 검사
2. 검증이 필요한 문장 하이라이트
3. 위험도 영양성분표 1~5단계 표시
4. 관련 기사 크로스체크 키워드 추천
5. 전체 기사 분석 결과 반환

## 폴더 구조

```text
news-risk-checker/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── routes/
│   │   └── analyze.py
│   └── services/
│       ├── article_extractor.py
│       ├── gemini_analyzer.py
│       └── gpt_analyzer.py
└── frontend/
    ├── package.json
    ├── index.html
    └── src/
        ├── App.jsx
        ├── App.css
        ├── main.jsx
        ├── api/
        │   └── analyzeApi.js
        └── components/
            ├── AiReportCard.jsx
            ├── ArticleViewer.jsx
            ├── RelatedQueries.jsx
            ├── RiskNutritionLabel.jsx
            ├── RiskSentenceList.jsx
            └── UrlInput.jsx
```

## 실행 방법

### 1. Backend 실행

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
```

`.env` 파일에 본인의 Gemini API Key를 넣으세요.

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

실행:

```bash
python app.py
```

Backend 주소:

```text
http://127.0.0.1:5000
```

### 2. Frontend 실행

새 터미널에서:

```bash
cd frontend
npm install
npm run dev
```

Frontend 주소:

```text
http://localhost:5173
```

## 동작 흐름

- `frontend/src/App.jsx`에서 기사 URL을 입력받고 `/api/analyze`로 POST 요청을 보냅니다.
- `backend/routes/analyze.py`는 `backend/services/article_extractor.py`로 기사 제목과 본문을 추출합니다.
- 추출된 기사 텍스트는 `backend/services/gemini_analyzer.py`에서 Gemini API로 분석되어 JSON 응답을 만듭니다.
- 프론트엔드는 AI 검사 결과, 위험 문장, 영양성분표, 관련 검색어를 화면에 표시합니다.

## 참고

현재 관련 기사 추천 기능은 실제 뉴스 검색 API가 아니라, Gemini 분석 결과에서 생성한 검색 키워드를 보여주는 MVP 방식입니다.

추후 개선 시 연결 가능한 API:

- Naver Search API
- Google Custom Search API
- Bing Search API
- SerpAPI
- NewsAPI
