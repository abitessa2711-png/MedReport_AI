import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'

export const api = axios.create({ baseURL })

export async function registerUser(email, password, fullName) {
  const { data } = await api.post('/auth/register', {
    email,
    password,
    full_name: fullName || null,
  })
  return data
}

export async function loginUser(email, password) {
  const { data } = await api.post('/auth/login', { email, password })
  return data
}

export async function getCurrentUser(email) {
  const { data } = await api.get('/auth/me', { params: { email } })
  return data
}

export async function uploadReport(file, age, gender, onProgress) {
  const formData = new FormData()
  formData.append('file', file)
  if (age) formData.append('age', age)
  if (gender) formData.append('gender', gender)
  const { data } = await api.post('/upload-report', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (evt) => {
      if (onProgress && evt.total) {
        onProgress(Math.round((evt.loaded / evt.total) * 100))
      }
    },
  })
  return data
}

export async function extractReport(reportId) {
  const { data } = await api.post('/extract-report', { report_id: reportId })
  return data
}

export async function analyzeReport(reportId, { userEmail, age, gender, symptoms, corrections } = {}) {
  const { data } = await api.post('/analyze-report', {
    report_id: reportId,
    user_email: userEmail || null,
    age: age ? Number(age) : null,
    gender: gender || null,
    symptoms: symptoms || null,
    corrections: corrections || null,
  })
  return data
}

export async function claimReport(reportId, userEmail) {
  const { data } = await api.post(`/reports/${reportId}/claim`, { user_email: userEmail })
  return data
}

export async function listReports(userEmail = null) {
  const params = userEmail ? { user_email: userEmail } : {}
  const { data } = await api.get('/reports', { params })
  return data
}

export async function getReport(reportId) {
  const { data } = await api.get(`/reports/${reportId}`)
  return data
}

export function extractErrorMessage(err) {
  return (
    err?.response?.data?.detail ||
    err?.message ||
    'Something went wrong. Please try again.'
  )
}
