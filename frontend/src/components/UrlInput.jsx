/* URL 입력 필드 */
function UrlInput({ url, setUrl, onAnalyze }) {
  return (
    <section className="url-box">
      <input
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="뉴스 기사 URL을 입력하세요"
        onKeyDown={(e) => {
          if (e.key === "Enter") onAnalyze();
        }}
      />
      <button onClick={onAnalyze}>분석하기</button>
    </section>
  );
}

export default UrlInput;
