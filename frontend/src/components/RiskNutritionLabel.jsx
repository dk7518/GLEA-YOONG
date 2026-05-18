/* 검증 위험도 영양성분표 */
function RiskNutritionLabel({ label = {} }) {
  const items = [
    ["인물/기관명 위험", label.entity_risk],
    ["핵심 수치 위험", label.number_risk],
    ["출처 불명확 위험", label.source_risk],
    ["선동적 표현 위험", label.sensational_risk],
    ["맥락 누락 위험", label.context_loss_risk],
  ];

  const getScore = (item) => {
    if (typeof item === "number") return item;
    return item?.score ?? 1;
  };

  const getRiskLabel = (item) => {
    if (typeof item === "number") return "";
    return item?.label ?? "알 수 없음";
  };

  const getExample = (item) => {
    if (typeof item === "number") {
      return "해당 항목에 대한 예시 설명이 아직 제공되지 않았습니다.";
    }
    return item?.example ?? "해당 항목에 대한 예시 설명이 제공되지 않았습니다.";
  };

  const getCriteria = (item) => {
    if (typeof item === "number") {
      return "점수 기준 설명이 아직 제공되지 않았습니다.";
    }
    return item?.criteria ?? "점수 기준 설명이 제공되지 않았습니다.";
  };

  return (
    <div className="card">
      <h3>검증 위험도 영양성분표</h3>

      <p className="nutrition-guide">
        각 점수는 사실 오류를 확정하는 값이 아니라, 해당 항목에 대해 검증이 얼마나 필요한지를 나타냅니다.
      </p>

      <div className="nutrition-list">
        {items.map(([name, item]) => {
          const score = getScore(item);
          const riskLabel = getRiskLabel(item);
          const example = getExample(item);
          const criteria = getCriteria(item);

          return (
            <div className={`nutrition-card border-level-${score}`} key={name}>
              <div className="nutrition-row">
                <span className="nutrition-name">{name}</span>

                <div className="bar">
                  <div
                    className={`bar-fill level-${score}`}
                    style={{ width: `${score * 20}%` }}
                  />
                </div>

                <b className="nutrition-score">{score}/5</b>
              </div>

              <p className="nutrition-detail">
                <b>등급:</b> {riskLabel}
              </p>

              <p className="nutrition-detail">
                <b>예시:</b> {example}
              </p>

              <p className="nutrition-detail">
                <b>기준:</b> {criteria}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default RiskNutritionLabel;