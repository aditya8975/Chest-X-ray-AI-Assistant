const BASE = '/api';

async function handle(res) {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      // ignore
    }
    throw new Error(detail);
  }
  return res.json();
}

export const api = {
  uploadStudy: (file, patientRef, modalityNote) => {
    const form = new FormData();
    form.append('file', file);
    if (patientRef) form.append('patient_ref', patientRef);
    if (modalityNote) form.append('modality_note', modalityNote);
    return fetch(`${BASE}/studies/upload`, { method: 'POST', body: form }).then(handle);
  },
  listStudies: (limit = 100) => fetch(`${BASE}/studies?limit=${limit}`).then(handle),
  getStudy: (id) => fetch(`${BASE}/studies/${id}`).then(handle),
  deleteStudy: (id) => fetch(`${BASE}/studies/${id}`, { method: 'DELETE' }).then(handle),
  dashboardStats: () => fetch(`${BASE}/dashboard/stats`).then(handle),
};

export function mediaUrl(path) {
  if (!path) return '';
  const idx = path.indexOf('/data/');
  if (idx !== -1) {
    const rel = path.slice(idx + 6); // strips through "data/"
    return `/media/${rel}`;
  }
  return path;
}
