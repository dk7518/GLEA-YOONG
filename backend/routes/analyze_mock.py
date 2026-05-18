from flask import Blueprint, request, jsonify
from services.article_extractor import extract_article

analyze_bp = Blueprint("analyze", __name__)

@analyze_bp.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL이 필요합니다."}), 400

    article = extract_article(url)

    if not article["text"]:
        return jsonify({"error": "기사 본문을 추출하지 못했습니다."}), 400

    first_sentence = article["text"].split(".")[0]
    if len(first_sentence) < 10:
        first_sentence = article["text"][:120]

    mock_analysis = {
        "article_title": article["title"],
        "summary": "이 기사는 특정 사건 또는 이슈에 대한 내용을 전달하고 있으며, 일부 핵심 주장과 수치 정보는 추가 검증이 필요합니다.",
        "ai_check_report": {
            "ai_probability": 62,
            "ai_label": "Mixed",
            "reason": "문장 구조가 비교적 일정하고 단정적인 표현이 일부 포함되어 있어 AI 보조 작성 가능성이 있습니다.",
            "perplexity_like_signal": "보통",
            "burstiness_signal": "낮음"
        },
        "overall_risk": {
            "score": 71,
            "level": 4,
            "label": "높음",
            "explanation": "기사 내 핵심 주장, 기관명, 수치성 정보, 출처 확인이 필요한 표현이 포함되어 있어 다른 기사나 공식 자료와의 크로스체크가 필요합니다."
        },
        "nutrition_label": {
            "entity_risk": 4,
            "number_risk": 4,
            "source_risk": 3,
            "sensational_risk": 3,
            "context_loss_risk": 4
        },
        "sentences_to_check": [
            {
                "sentence": first_sentence,
                "risk_level": 4,
                "risk_label": "높음",
                "risk_factors": ["핵심 주장", "출처 확인 필요"],
                "reason": "기사의 핵심 내용을 담고 있는 문장으로, 다른 언론 보도나 공식 발표 자료와 대조할 필요가 있습니다.",
                "suggested_check": "동일 사건을 다룬 다른 언론 기사, 정부/기관 공식 발표, 원문 자료와 비교하세요."
            }
        ],
        "related_article_queries": [
            {
                "query": article["title"],
                "purpose": "같은 제목 또는 같은 사건을 다룬 다른 언론 보도를 찾기 위함입니다."
            },
            {
                "query": article["title"] + " 공식 발표",
                "purpose": "공식 기관 자료와 기사 내용을 비교하기 위함입니다."
            },
            {
                "query": article["title"] + " 팩트체크",
                "purpose": "이미 검증된 팩트체크 자료가 있는지 확인하기 위함입니다."
            }
        ]
    }

    return jsonify({
        "article": article,
        "analysis": mock_analysis
    })