export async function analyzeArticle(url) {
  const response = await fetch("http://127.0.0.1:5000/api/analyze", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ url }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "분석에 실패했습니다.");
  }

  return data;
}
