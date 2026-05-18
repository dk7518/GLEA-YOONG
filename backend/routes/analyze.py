from flask import Blueprint, request, jsonify
from services.article_extractor import extract_article
from services.gemini_analyzer import analyze_article_with_gpt

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

    analysis = analyze_article_with_gpt(
        title=article["title"],
        text=article["text"],
        url=article["url"]
    )

    return jsonify({
        "article": article,
        "analysis": analysis
    })