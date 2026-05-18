/* 검증이 필요한 문장 */
function RiskSentenceList({ sentences = [] }) {
  return (
    <div className="card">
      <h3>검증이 필요한 문장</h3>

      {sentences.length === 0 && (
        <p>검증이 필요한 문장이 크게 발견되지 않았습니다.</p>
      )}

      {sentences.map((item, index) => (
        <div className={`risk-card border-level-${item.risk_level}`} key={index}>
          <p className="risk-sentence">"{item.sentence}"</p>
          <p><b>위험도:</b> {item.risk_label} ({item.risk_level}/5)</p>
          <p><b>위험 요인:</b> {(item.risk_factors || []).join(", ")}</p>
          <p><b>검증 방법:</b> {item.suggested_check}</p>
        </div>
      ))}
    </div>
  );
}

export default RiskSentenceList;