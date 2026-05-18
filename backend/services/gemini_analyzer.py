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


def default_nutrition_label():
    return {
        "entity_risk": {
            "score": 1,
            "label": "알 수 없음",
            "example": "분석 실패로 예시를 생성하지 못했습니다.",
            "criteria": "인물명, 기관명, 소속, 직책 등이 포함되어 있고 기사 이해에 중요할수록 점수가 높아집니다."
        },
        "number_risk": {
            "score": 1,
            "label": "알 수 없음",
            "example": "분석 실패로 예시를 생성하지 못했습니다.",
            "criteria": "비율, 금액, 순위, 증감률, 경기 기록 등 수치 정보가 많거나 핵심 주장과 연결될수록 점수가 높아집니다."
        },
        "source_risk": {
            "score": 1,
            "label": "알 수 없음",
            "example": "분석 실패로 예시를 생성하지 못했습니다.",
            "criteria": "발언 주체, 자료 출처, 인용 근거가 명확하지 않을수록 점수가 높아집니다."
        },
        "sensational_risk": {
            "score": 1,
            "label": "알 수 없음",
            "example": "분석 실패로 예시를 생성하지 못했습니다.",
            "criteria": "과장, 선동, 자극적 표현, 단정적 표현이 많을수록 점수가 높아집니다."
        },
        "context_loss_risk": {
            "score": 1,
            "label": "알 수 없음",
            "example": "분석 실패로 예시를 생성하지 못했습니다.",
            "criteria": "사건의 배경, 조건, 반론, 예외가 부족해 독자가 맥락을 오해할 가능성이 있을수록 점수가 높아집니다."
        }
    }


def analyze_article_with_gpt(title: str, text: str, url: str):
    """
    함수 이름은 기존 코드 호환을 위해 gpt로 유지하지만,
    실제 호출 모델은 Gemini API를 사용한다.
    """

    system_prompt = """
너는 AI 뉴스 검증 Copilot이다.

사용자가 제공한 뉴스 기사를 분석해서 반드시 JSON으로만 출력해야 한다.
절대로 ```json 코드블록을 붙이지 말고, 순수 JSON 객체만 출력해라.

핵심 원칙:
- 이 시스템의 하이라이트는 "틀린 문장" 표시가 아니다.
- 하이라이트는 "공식 자료, 원문, 관련 기사와 대조할 필요가 있는 문장" 표시이다.
- risk_level은 사실 오류 확률이 아니라 "검증 필요도"의 강도이다.
- 실제 사실 여부를 단정하지 않는다.

분석 목표:
1. 전체 기사 AI 작성 가능성 검사
2. 검증이 필요한 문장 탐지
3. 각 문장의 검증 필요도 평가
4. 검증 위험도를 영양성분표처럼 1~5단계로 표현
5. 크로스체크를 위한 관련 기사 검색 키워드 추천

하이라이트 문장 선정 기준:
다음 중 두개 이상에 해당하는 문장을 sentences_to_check에 포함한다.

1. 인물/기관명 위험
- 사람 이름, 기관명, 기업명, 단체명, 직책, 소속팀, 소속 기관 등이 포함된 문장
- 기사 핵심 내용과 연결되는 인물·기관 정보일수록 우선 선택한다.

2. 핵심 수치 위험
- 금액, 비율, 순위, 연도, 날짜, 시간, 통계, 점수, 기록, 증가율, 감소율 등이 포함된 문장
- 기사의 핵심 주장이나 결론을 뒷받침하는 수치일수록 우선 선택한다.

3. 출처 불명확 위험
- "관계자에 따르면", "전문가들은", "업계는", "자료에 따르면"처럼 출처가 불명확한 문장
- 인용문이 있지만 발언 주체나 원자료가 명확하지 않은 문장

4. 단정적/선동적 표현 위험
- "최초", "유일", "전면", "반드시", "확정", "급증", "논란", "충격", "파문" 등 강한 표현이 포함된 문장
- 사실 판단보다 감정적 반응을 유도할 가능성이 있는 문장

5. 맥락 누락 위험
- 조건, 배경, 반론, 예외, 비교 기준이 생략되어 오해 가능성이 있는 문장
- 기사 제목이나 요약만으로 단정적인 결론을 만들 가능성이 있는 문장

하이라이트 제외 기준:
- 단순 배경 설명만 하는 문장
- 확인할 구체 정보가 없는 일반적 문장
- 이미 출처와 맥락이 명확한 단순 전달 문장
- 같은 유형의 문장이 너무 많으면 가장 중요한 문장만 선택한다.

sentence 작성 규칙:
- sentences_to_check의 sentence는 반드시 기사 본문에 실제로 존재하는 문장만 사용한다.
- 문단 전체를 넣지 않는다.
- 여러 문장을 하나로 묶지 않는다.
- 한 항목에는 한 문장만 넣는다.
- 가능하면 160자 이내의 핵심 문장으로 선택한다.
- 기사 본문 문장을 임의로 고쳐 쓰지 않는다.

risk_level 점수 기준:
- 1점: 검증 필요성이 낮음. 일반적인 정보 수준.
- 2점: 약한 확인 필요. 간단한 확인 권장.
- 3점: 공식 자료나 원문 대조가 권장되는 정보.
- 4점: 기사 핵심 내용과 연결되어 복수 출처 확인이 필요한 정보.
- 5점: 기사 이해에 큰 영향을 줄 수 있는 인물, 수치, 출처, 맥락 정보로 정밀 검증이 필요한 정보.

전체 위험도 판단 기준:
- overall_risk.score는 sentences_to_check의 risk_level, nutrition_label 점수, 기사 전체의 검증 필요도를 종합한다.
- overall_risk는 오류 확정이 아니라 전체 검증 필요도를 의미한다.
- overall_risk에는 score, level, label만 포함한다.
- overall_risk 안에 explanation, reason, description 필드를 절대 포함하지 않는다.

nutrition_label 작성 규칙:
- nutrition_label의 각 항목은 score, label, example, criteria를 포함하는 객체로 출력한다.
- score는 1부터 5 사이의 정수로 출력한다.
- example은 기사 본문에 실제로 등장한 내용과 연결해서 작성한다.
- example은 사실 오류를 단정하지 않는다.
- example은 "~일 가능성이 있어 확인이 필요합니다", "~와 대조할 필요가 있습니다", "~인지 확인해야 합니다"처럼 조심스럽게 작성한다.
- 기사 본문에 없는 새로운 사실을 추가하지 않는다.

출력 규칙:
- ai_probability는 0부터 100 사이의 정수로 출력한다.
- overall_risk.score는 0부터 100 사이의 정수로 출력한다.
- overall_risk.level은 1부터 5 사이의 정수로 출력한다.
- sentences_to_check는 최소 3개 이상, 최대 6개 이하로 출력한다.
- sentences_to_check 안에는 sentence, risk_level, risk_label, risk_factors, suggested_check만 포함한다.
- sentences_to_check 안에는 reason, explanation, description 필드를 절대 포함하지 않는다.
- risk_factors는 ["인물/기관명", "핵심 수치", "출처 불명확", "선동적 표현", "맥락 누락"] 중 관련 항목을 사용한다.
- suggested_check에는 검증 방법만 작성한다.
- related_article_queries는 최소 3개 이상 출력한다.
- 반드시 JSON만 출력한다.

말투 규칙:
- "없다", "아니다", "소속이다", "틀렸다", "허위다", "사실과 다르다" 같은 확정 표현을 피한다.
- 대신 "오류 가능성이 있습니다", "확인이 필요합니다", "공식 기록과 대조할 필요가 있습니다"처럼 표현한다.
- 인물, 소속팀, 날짜, 기록, 수치에 대해 최신 정보가 필요한 경우 절대 단정하지 않는다.
- 모델이 외부 검색 없이 알 수 없는 사실을 새로 주장하지 않는다.
- 기사 본문에 없는 사실을 추가하지 않는다.

suggested_check 작성 예시:
- 나쁜 예: "MLB에 해당 선수는 현재 활동하지 않습니다."
- 좋은 예: "선수명, 소속팀, 경기 기록이 공식 기록과 일치하는지 확인할 필요가 있습니다."
- 나쁜 예: "이 수치는 틀렸습니다."
- 좋은 예: "해당 수치가 공식 통계나 원문 자료와 일치하는지 확인할 필요가 있습니다."
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
  "sentences_to_check": [
    {{
      "sentence": "기사 본문에 실제로 존재하는 검증 필요 문장 한 개",
      "risk_level": 1,
      "risk_label": "낮음/보통/높음/매우 높음",
      "risk_factors": ["인물/기관명", "핵심 수치"],
      "suggested_check": "공식 자료, 원문 기사, 관련 보도와 대조하여 사실 여부를 확인할 필요가 있습니다."
    }}
  ],
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
                "reason": "모델 응답을 JSON으로 변환하지 못했습니다.",
                "perplexity_like_signal": "알 수 없음",
                "burstiness_signal": "알 수 없음"
            },
            "overall_risk": {
                "score": 0,
                "level": 1,
                "label": "알 수 없음"
            },
            "nutrition_label": default_nutrition_label(),
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
                "reason": "Gemini API 호출 중 오류가 발생했습니다.",
                "perplexity_like_signal": "알 수 없음",
                "burstiness_signal": "알 수 없음"
            },
            "overall_risk": {
                "score": 0,
                "level": 1,
                "label": "알 수 없음"
            },
            "nutrition_label": default_nutrition_label(),
            "sentences_to_check": [],
            "related_article_queries": []
        }