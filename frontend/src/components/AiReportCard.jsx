/* 전체 기사 AI 검사표 */
function AiReportCard({ aiReport }) {
  return (
    <div className="card">
      <h3>전체 기사 AI 검사표</h3>

      <div className="score-box">
        <span>AI 작성 가능성</span>
        <strong>{aiReport.ai_probability}%</strong>
      </div>

      <p><b>판정:</b> {aiReport.ai_label}</p>
      <p><b>판단 이유:</b> {aiReport.reason}</p>
      <p><b>Perplexity 신호:</b> {aiReport.perplexity_like_signal}</p>
      <p><b>Burstiness 신호:</b> {aiReport.burstiness_signal}</p>
    </div>
  );
}

export default AiReportCard;