/* 기사 뷰어 */
function ArticleViewer({ article, riskySentences = [] }) {
  const paragraphs = article.text.split("\n").filter(Boolean);

  const getRiskInfo = (paragraph) => {
    return riskySentences.find((item) => paragraph.includes(item.sentence));
  };

  return (
    <div className="article-card">
      <h2>{article.title}</h2>
      <p className="article-url">{article.url}</p>

      <div className="article-body">
        {paragraphs.map((paragraph, index) => {
          const riskInfo = getRiskInfo(paragraph);

          if (!riskInfo) {
            return <p key={index}>{paragraph}</p>;
          }

          return (
            <p key={index} className={`highlight level-${riskInfo.risk_level}`}>
              {paragraph}
              <span className={`risk-badge level-${riskInfo.risk_level}`}>
                위험도 {riskInfo.risk_level}/5
              </span>
            </p>
          );
        })}
      </div>
    </div>
  );
}

export default ArticleViewer;
