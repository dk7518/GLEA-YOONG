import { useState } from "react";
import { analyzeArticle } from "./api/analyzeApi";
import UrlInput from "./components/UrlInput";
import ArticleViewer from "./components/ArticleViewer";
import AiReportCard from "./components/AiReportCard";
import RiskNutritionLabel from "./components/RiskNutritionLabel";
import RiskSentenceList from "./components/RiskSentenceList";
import RelatedQueries from "./components/RelatedQueries";

function App() {
  const [url, setUrl] = useState("");
  const [article, setArticle] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!url.trim()) {
      alert("기사 URL을 입력해주세요.");
      return;
    }

    setLoading(true);
    setArticle(null);
    setAnalysis(null);

    try {
      const data = await analyzeArticle(url);
      setArticle(data.article);
      setAnalysis(data.analysis);
    } catch (error) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>AI 뉴스 검증 Copilot</h1>
        <p>
          기사 URL을 입력하면 AI 작성 가능성, 검증 위험도, 관련 기사
          크로스체크 키워드를 분석합니다.
        </p>
      </header>

      <UrlInput url={url} setUrl={setUrl} onAnalyze={handleAnalyze} />

      {loading && <div className="loading">기사 분석 중...</div>}

      {article && analysis && (
        <main className="layout">
          <section className="left-panel">
            <ArticleViewer
              article={article}
              riskySentences={analysis.sentences_to_check || []}
            />
          </section>

          <aside className="right-panel">
            <AiReportCard
              aiReport={analysis.ai_check_report}
              overallRisk={analysis.overall_risk}
            />

            <RiskNutritionLabel label={analysis.nutrition_label} />

            <RiskSentenceList sentences={analysis.sentences_to_check || []} />

            <RelatedQueries queries={analysis.related_article_queries || []} />
          </aside>
        </main>
      )}
    </div>
  );
}

export default App;
