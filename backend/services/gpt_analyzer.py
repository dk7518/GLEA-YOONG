import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_article_with_gpt(title: str, text: str, url: str):
    system_prompt = """
너는 AI 뉴스 검증 Copilot이다.

사용자가 제공한 뉴스 기사를 분석해 다음 결과를 JSON으로 출력해야 한다.

분석 항목:
1. 전체 기사 AI 작성 가능성
2. 검증이 필요한 문장
3. 문장별 위험도 1~5단계
4. 위험도 영양성분표
5. 왜 위험한지 설명
6. 크로스체크용 관련 기사 검색어

위험도 기준:
- 인물명/기관명 오류 가능성
- 핵심 수치 오류 가능성
- 날짜/통계 오류 가능성
- 출처 불명확성
- 자극적 표현
- 단정적 표현
- 인용문 출처 불명확
- AI 요약으로 인한 맥락 누락 가능성

위험도 등급:
1 = 낮음
2 = 약간 낮음
3 = 보통
4 = 높음
5 = 매우 높음

반드시 JSON만 출력해라.
"""

    user_prompt = f"""
기사 URL:
{url}

기사 제목:
{title}

기사 본문:
{text[:8000]}

아래 형식으로만 JSON을 출력해.

{{
  "article_title": "{title}",
  "summary": "기사 핵심 요약",
  "ai_check_report": {{
    "ai_probability": 0,
    "ai_label": "Human-like / Mixed / AI-like",
    "reason": "AI 작성 가능성 판단 이유",
    "perplexity_like_signal": "낮음/보통/높음",
    "burstiness_signal": "낮음/보통/높음"
  }},
  "overall_risk": {{
    "score": 0,
    "level": 1,
    "label": "낮음/보통/높음/매우 높음",
    "explanation": "전체 기사 위험도 설명"
  }},
  "nutrition_label": {{
    "entity_risk": 1,
    "number_risk": 1,
    "source_risk": 1,
    "sensational_risk": 1,
    "context_loss_risk": 1
  }},
  "sentences_to_check": [
    {{
      "sentence": "검증이 필요한 문장",
      "risk_level": 1,
      "risk_label": "낮음/보통/높음/매우 높음",
      "risk_factors": ["핵심 수치", "출처 불명확"],
      "reason": "왜 위험한지",
      "suggested_check": "무엇과 대조하면 좋은지"
    }}
  ],
  "related_article_queries": [
    {{
      "query": "검색 키워드",
      "purpose": "왜 이 키워드로 검색해야 하는지"
    }}
  ]
}}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )

    raw = response.output_text

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "article_title": title,
            "summary": "분석 결과 파싱 실패",
            "ai_check_report": {
                "ai_probability": 0,
                "ai_label": "Unknown",
                "reason": raw,
                "perplexity_like_signal": "알 수 없음",
                "burstiness_signal": "알 수 없음"
            },
            "overall_risk": {
                "score": 0,
                "level": 1,
                "label": "알 수 없음",
                "explanation": "JSON 파싱에 실패했습니다."
            },
            "nutrition_label": {
                "entity_risk": 1,
                "number_risk": 1,
                "source_risk": 1,
                "sensational_risk": 1,
                "context_loss_risk": 1
            },
            "sentences_to_check": [],
            "related_article_queries": []
        }
