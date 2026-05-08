const state = { token: "", base: "http://127.0.0.1:8765" };

function setOutput(x) {
  document.getElementById("out").textContent = typeof x === "string" ? x : JSON.stringify(x, null, 2);
}

async function api(path, options = {}) {
  state.token = document.getElementById("token").value;
  state.base = document.getElementById("base").value;
  options.headers = Object.assign({
    "Content-Type": "application/json",
    "Authorization": "Bearer " + state.token,
  }, options.headers || {});
  const res = await fetch(state.base + path, options);
  const text = await res.text();
  try { return JSON.parse(text); } catch { return text; }
}

async function login() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const base = document.getElementById("base").value;
  const res = await fetch(base + "/auth/login", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({username, password})
  });
  const data = await res.json();
  if (data.token) document.getElementById("token").value = data.token;
  setOutput(data);
}

async function submitTask() {
  const instruction = document.getElementById("instruction").value;
  setOutput(await api("/tasks", {method: "POST", body: JSON.stringify({instruction})}));
}

async function loadTasks() { setOutput(await api("/tasks")); }
async function runWorker() { setOutput(await api("/worker/run-once", {method: "POST", body: "{}"})); }
async function metrics() { setOutput(await api("/metrics")); }
async function latestCerts() { setOutput(await api("/certificates/latest")); }
async function gitStatus() { setOutput(await api("/git/status")); }
