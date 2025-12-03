const API_BASE_URL = "http://127.0.0.1:8000";

async function apiRequest(endpoint, method = "GET", body = null, token = null) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const options = { method, headers };
  if (body) options.body = JSON.stringify(body);

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || data.message || "Lỗi API");
    }

    return data;
  } catch (error) {
    console.error("API error:", error);
    throw error;
  }
}

export async function register(fullname, email, password, income) {
  return apiRequest("/register", "POST", {
    fullname,
    email,
    password,
    income,
  });
}

export async function login(email, password) {
  return apiRequest("/login", "POST", { email, password});
}

export async function getExpenses(userId) {
  return apiRequest(`/expenses/${userId}`, "GET");
}

export async function addExpense(user_id, date, category, amount, note) {
  return apiRequest("/expenses", "POST", {
    user_id,
    date,
    category,
    amount,
    note,
  });
}

export async function updateExpense(expense_id, data) {
  return apiRequest(`/expenses/${expense_id}`, "PUT", data);
}

export async function deleteExpense(expense_id) {
  return apiRequest(`/expenses/${expense_id}`, "DELETE");
}

export async function getExpensesByMonth(userId, year, month) {
  return apiRequest(`/expenses/${userId}/detail?year=${year}&month=${month}`, "GET");
}
