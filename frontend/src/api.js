const API_BASE = import.meta.env.VITE_API_BASE || "/_/backend";

export async function processClaim(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/process-claim`, { method: "POST", body: formData });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Server error: ${res.status}`);
  }
  return res.json();
}

export async function fetchPolicies() {
  const res = await fetch(`${API_BASE}/policies`);
  if (!res.ok) throw new Error("Failed to load policies");
  return res.json();
}

export async function uploadPolicy(file, policyType) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("policy_type", policyType);
  const res = await fetch(`${API_BASE}/upload-policy`, { method: "POST", body: formData });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Upload failed: ${res.status}`);
  }
  return res.json();
}

export async function fetchSampleClaimFile(filename) {
  const res = await fetch(`${API_BASE}/samples/${filename}`);
  if (!res.ok) throw new Error(`Could not fetch sample: ${filename}`);
  const blob = await res.blob();
  return new File([blob], filename, { type: "application/pdf" });
}
