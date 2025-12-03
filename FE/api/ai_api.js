const API_BASE_URL = "https://openrouter.ai/api/v1/chat/";

async function apiRequest(endpoint, method = "GET", body = null, token = null) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const options = { method, headers };
  if (body) options.body = JSON.stringify(body);

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Lỗi API");
    }

    return data;
  } catch (error) {
    console.error("API error:", error);
    throw error;
  }
}

export async function sendMessage(model, messages) {
  const token =
    "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";

  const body = {
    model,
    messages,
  };

  const data = await apiRequest("completions", "POST", body, token);

  const content = data?.choices?.[0]?.message?.content || "";
  return { content };
}

export function createMessage(role, content) {
  return { role, content };
}
