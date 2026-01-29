const API_BASE = import.meta.env.VITE_API_URL || "";

async function fetchJson(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function getCompanies() {
  return fetchJson("/api/companies");
}

export async function getSuppliers() {
  return fetchJson("/api/suppliers");
}

export async function getPorts() {
  return fetchJson("/api/ports");
}

export async function getSupplyChain(companyId, depth = 4) {
  return fetchJson("/api/supply-chain", {
    method: "POST",
    body: JSON.stringify({ company_id: companyId, depth }),
  });
}

export async function getImpact(scenario, targetId) {
  return fetchJson("/api/impact", {
    method: "POST",
    body: JSON.stringify({ scenario, target_id: targetId }),
  });
}
