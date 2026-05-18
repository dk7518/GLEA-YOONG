import os
import json
import re
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI


# Load .env from backend/.env
BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY가 없습니다. backend/.env 파일을 확인하세요.")


# Use Gemini through OpenAI-compatible endpoint
client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


def clean_json_text(raw_text: str) -> str:
    """
    Gemini가 ```json ... ``` 형태로 응답하는 경우가 있어서
    순수 JSON 부분만 추출하는 함수.
    """
    raw_text = raw_text.strip()

    # Remove markdown code block markers
    raw_text = re.sub(r"^```json\s*", "", raw_text)
    raw_text = re.sub(r"^```\s*", "", raw_text)
    raw_text = re.sub(r"\s*```$", "", raw_text)

    # Extract only the outermost JSON object
    start = raw_text.find("{")
    end = raw_text.rfind("}")

    if start != -1 and end != -1 and end > start:
        raw_text = raw_text[start:end + 1]

    return raw_text


def analyze_article_with_gpt(title: str, text: str, url: str):
    """
    함수 이름은 기존 코드 호환을 위해 gpt로 유지하지만,
    실제 호출 모델은 Gemini API를 사용한다.
    """

    system_prompt = """
너는 AI 뉴스 검증 Copilot이다.

사용자가 제공한 뉴스 기사를 분석해서 반드시 JSON으로만 출력해야 한다.
절대로 ```json 코드블록을 붙이지 말고, 순수 JSON 객체만 출력해라.

분석 목표:
1. 전체 기사 AI 작성 가능성 검사
2. 검증이 필요한 문장 탐지
3. 각 문장의 검증 위험도 평가
4. 위험도를 영양성분표처럼 1~5단계로 표현
5. 크로스체크를 위한 관련 기사 검색 키워드 추천

위험도 판단 기준:
- 인물/기관명 오류 가능성
- 핵심 수치 오류 가능성
- 날짜/시간/통계 오류 가능성
- 출처 불명확성
- 자극적/선동적 표현
- 단정적 표현
- 인용문 출처 불명확
- AI 요약으로 인한 맥락 누락 가능성

점수 기준:
- 1점: 위험 신호가 거의 없음. 일반적인 정보 수준.
- 2점: 약한 위험 신호가 있음. 간단한 확인 권장.
- 3점: 검증이 필요한 정보가 있음. 공식 자료나 원문 대조 필요.
- 4점: 오류 가능성이 비교적 높은 정보가 있음. 복수 출처 확인 필요.
- 5점: 핵심 사실 오류 가능성이 높거나, 수치/인물/출처 문제가 기사 이해에 큰 영향을 줄 수 있음. 반드시 정밀 검증 필요.

중요한 출력 규칙:
- ai_probability는 0부터 100 사이의 정수로 출력한다.
- overall_risk.score는 0부터 100 사이의 정수로 출력한다.
- overall_risk.level은 1부터 5 사이의 정수로 출력한다.
- overall_risk에는 score, level, label만 포함한다.
- overall_risk 안에 explanation, reason, description 같은 설명 필드는 절대 포함하지 않는다.
- 전체 위험도에 대한 긴 자연어 설명 문단은 절대 작성하지 않는다.
- nutrition_label의 각 항목은 score, label, example, criteria를 포함하는 객체로 출력한다.
- nutrition_label의 score는 1부터 5 사이의 정수로 출력한다.
- sentences_to_check는 최소 3개 이상 출력한다.
- sentences_to_check 안에는 sentence, risk_level, risk_label, risk_factors, suggested_check만 포함한다.
- sentences_to_check 안에는 reason, explanation, description 필드를 절대 포함하지 않는다.
- 위험 근거는 risk_factors 배열에 키워드 형태로만 작성한다.
- 검증 방법은 suggested_check에만 작성한다.
- related_article_queries는 최소 3개 이상 출력한다.
- 기사 본문에 없는 사실을 추측하거나 새로 만들어내지 않는다.
- 반드시 JSON만 출력한다.

말투 규칙:
- 실제 사실 여부를 단정하지 않는다.
- “없다”, “아니다”, “소속이다”, “틀렸다”, “허위다” 같은 확정 표현을 피한다.
- 대신 “오류 가능성이 있습니다”, “확인이 필요합니다”, “공식 기록과 대조할 필요가 있습니다”처럼 표현한다.
- 인물, 소속팀, 날짜, 기록, 수치에 대해 최신 정보가 필요한 경우 절대 단정하지 않는다.
- 모델이 외부 검색 없이 알 수 없는 사실을 새로 주장하지 않는다.
- 기사 본문에 없는 사실을 추가하지 않는다.

영양성분표 example 작성 규칙:
- example은 고정 문구를 그대로 반복하지 말고, 기사 본문에 실제로 등장한 내용과 연결해서 작성한다.
- 단, 사실 오류를 단정하지 않는다.
- “틀렸습니다”, “존재하지 않습니다”, “소속입니다”, “허위입니다” 같은 확정 표현을 쓰지 않는다.
- “~일 가능성이 있어 확인이 필요합니다”, “~와 대조할 필요가 있습니다”, “~인지 확인해야 합니다”처럼 조심스럽게 작성한다.
- 기사 본문에 없는 새로운 사실을 추가하지 않는다.
"""

    user_prompt = f"""
기사 URL:
{url}

기사 제목:
{title}

기사 본문:
{text[:8000]}

아래 JSON 형식으로만 답변해.

{{
  "article_title": "기사 제목",
  "summary": "기사 핵심 요약",
  "ai_check_report": {{
    "ai_probability": 0,
    "ai_label": "Human-like / Mixed / AI-like",
    "reason": "AI 작성 가능성 판단 이유. 단, 사실 여부를 단정하지 말고 문체적 특징 중심으로만 설명",
    "perplexity_like_signal": "낮음/보통/높음",
    "burstiness_signal": "낮음/보통/높음"
  }},
  "overall_risk": {{
    "score": 0,
    "level": 1,
    "label": "낮음/보통/높음/매우 높음"
  }},
  "nutrition_label": {{
  "entity_risk": {{
    "score": 1,
    "label": "낮음/보통/높음/매우 높음",
    "example": "기사에 등장한 인물명, 기관명, 소속, 직책 중 확인이 필요한 내용을 조심스러운 표현으로 작성",
    "criteria": "인물명, 기관명, 소속, 직책 등이 포함되어 있고 기사 이해에 중요할수록 점수가 높아짐"
  }},
  "number_risk": {{
    "score": 1,
    "label": "낮음/보통/높음/매우 높음",
    "example": "기사에 등장한 수치, 통계, 기록, 비율 중 확인이 필요한 내용을 조심스러운 표현으로 작성",
    "criteria": "비율, 금액, 순위, 증감률, 경기 기록 등 수치 정보가 많거나 핵심 주장과 연결될수록 점수가 높아짐"
  }},
  "source_risk": {{
    "score": 1,
    "label": "낮음/보통/높음/매우 높음",
    "example": "기사에서 출처나 근거가 불명확해 확인이 필요한 부분을 조심스러운 표현으로 작성",
    "criteria": "발언 주체, 자료 출처, 인용 근거가 명확하지 않을수록 점수가 높아짐"
  }},
  "sensational_risk": {{
    "score": 1,
    "label": "낮음/보통/높음/매우 높음",
    "example": "기사에서 강한 표현, 단정적 표현, 자극적 표현이 사용된 부분을 조심스러운 표현으로 작성",
    "criteria": "과장, 선동, 자극적 표현, 단정적 표현이 많을수록 점수가 높아짐"
  }},
  "context_loss_risk": {{
    "score": 1,
    "label": "낮음/보통/높음/매우 높음",
    "example": "기사에서 배경, 조건, 반론, 예외 등이 생략되었을 가능성이 있는 부분을 조심스러운 표현으로 작성",
    "criteria": "사건의 배경, 조건, 반론, 예외가 부족해 독자가 맥락을 오해할 가능성이 있을수록 점수가 높아짐"
  }}
}},
  "related_article_queries": [
    {{
      "query": "검색하면 좋은 관련 기사 키워드",
      "purpose": "해당 내용의 사실 관계를 복수 출처와 대조하기 위함"
    }}
  ]
}}
"""

    try:
        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )

        raw = response.choices[0].message.content
        cleaned = clean_json_text(raw)

        return json.loads(cleaned)

    except json.JSONDecodeError as e:
        print("JSON parsing error:", e)
        print("Raw model output:", raw)

        return {
            "article_title": title,
            "summary": "JSON 파싱 실패",
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
                "explanation": "모델 응답을 JSON으로 변환하지 못했습니다."
            },
            "nutrition_label": {{
  "entity_risk": {{
    "score": 1,
    "label": "낮음/보통/높음/매우 높음",
    "example": "기사에 등장한 인물명, 기관명, 소속, 직책 중 확인이 필요한 내용을 조심스러운 표현으로 작성",
    "criteria": "인물명, 기관명, 소속, 직책 등이 포함되어 있고 기사 이해에 중요할수록 점수가 높아짐"
  }},
  "number_risk": {{
    "score": 1,
    "label": "낮음/보통/높음/매우 높음",
    "example": "기사에 등장한 수치, 통계, 기록, 비율 중 확인이 필요한 내용을 조심스러운 표현으로 작성",
    "criteria": "비율, 금액, 순위, 증감률, 경기 기록 등 수치 정보가 많거나 핵심 주장과 연결될수록 점수가 높아짐"
  }},
  "source_risk": {{
    "score": 1,
    "label": "낮음/보통/높음/매우 높음",
    "example": "기사에서 출처나 근거가 불명확해 확인이 필요한 부분을 조심스러운 표현으로 작성",
    "criteria": "발언 주체, 자료 출처, 인용 근거가 명확하지 않을수록 점수가 높아짐"
  }},
  "sensational_risk": {{
    "score": 1,
    "label": "낮음/보통/높음/매우 높음",
    "example": "기사에서 강한 표현, 단정적 표현, 자극적 표현이 사용된 부분을 조심스러운 표현으로 작성",
    "criteria": "과장, 선동, 자극적 표현, 단정적 표현이 많을수록 점수가 높아짐"
  }},
  "context_loss_risk": {{
    "score": 1,
    "label": "낮음/보통/높음/매우 높음",
    "example": "기사에서 배경, 조건, 반론, 예외 등이 생략되었을 가능성이 있는 부분을 조심스러운 표현으로 작성",
    "criteria": "사건의 배경, 조건, 반론, 예외가 부족해 독자가 맥락을 오해할 가능성이 있을수록 점수가 높아짐"
  }}
}},
            "sentences_to_check": [],
            "related_article_queries": []
        }

    except Exception as e:
        print("Gemini API error:", e)

        return {
            "article_title": title,
            "summary": "API 호출 실패",
            "ai_check_report": {
                "ai_probability": 0,
                "ai_label": "Unknown",
                "reason": str(e),
                "perplexity_like_signal": "알 수 없음",
                "burstiness_signal": "알 수 없음"
            },
            "overall_risk": {
                "score": 0,
                "level": 1,
                "label": "알 수 없음",
                "explanation": "Gemini API 호출 중 오류가 발생했습니다."
            },
            "nutrition_label": {{
  "entity_risk": {{
    "score": 1,
    "label": "낮음/보통/높음/매우 높음",
    "example": "기사에 등장한 인물명, 기관명, 소속, 직책 중 확인이 필요한 내용을 조심스러운 표현으로 작성",
    "criteria": "인물명, 기관명, 소속, 직책 등이 포함되어 있고 기사 이해에 중요할수록 점수가 높아짐"
  }},
  "number_risk": {{
    "score": 1,
    "label": "낮음/보통/높음/매우 높음",
    "example": "기사에 등장한 수치, 통계, 기록, 비율 중 확인이 필요한 내용을 조심스러운 표현으로 작성",
    "criteria": "비율, 금액, 순위, 증감률, 경기 기록 등 수치 정보가 많거나 핵심 주장과 연결될수록 점수가 높아짐"
  }},
  "source_risk": {{
    "score": 1,
    "label": "낮음/보통/높음/매우 높음",
    "example": "기사에서 출처나 근거가 불명확해 확인이 필요한 부분을 조심스러운 표현으로 작성",
    "criteria": "발언 주체, 자료 출처, 인용 근거가 명확하지 않을수록 점수가 높아짐"
  }},
  "sensational_risk": {{
    "score": 1,
    "label": "낮음/보통/높음/매우 높음",
    "example": "기사에서 강한 표현, 단정적 표현, 자극적 표현이 사용된 부분을 조심스러운 표현으로 작성",
    "criteria": "과장, 선동, 자극적 표현, 단정적 표현이 많을수록 점수가 높아짐"
  }},
  "context_loss_risk": {{
    "score": 1,
    "label": "낮음/보통/높음/매우 높음",
    "example": "기사에서 배경, 조건, 반론, 예외 등이 생략되었을 가능성이 있는 부분을 조심스러운 표현으로 작성",
    "criteria": "사건의 배경, 조건, 반론, 예외가 부족해 독자가 맥락을 오해할 가능성이 있을수록 점수가 높아짐"
  }}
}},
            "sentences_to_check": [],
            "related_article_queries": []
        }