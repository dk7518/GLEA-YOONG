/* 관련 내용 다른 기사 추천 */
function RelatedQueries({ queries = [] }) {
  return (
    <div className="card">
      <h3>크로스체크 키워드 검색</h3>

      {queries.length === 0 && <p>추천 검색어가 없습니다.</p>}

      {queries.map((item, index) => (
        <div className="query-card" key={index}>
          <p><b>{item.query}</b></p>
          <p>{item.purpose}</p>
          <a
            href={`https://www.google.com/search?q=${encodeURIComponent(item.query)}`}
            target="_blank"
            rel="noreferrer"
          >
            Google에서 관련 기사 검색
          </a>
        </div>
      ))}
    </div>
  );
}

export default RelatedQueries;
