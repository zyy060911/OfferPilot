/**
 * Axios instance for binary/file download requests.
 * Does NOT strip the Result envelope; returns the full response.
 */
import axios from 'axios'
import { useUserStore } from '../store/user'

const downloadRequest = axios.create({
  baseURL: '/api',
  timeout: 60000,
  responseType: 'blob',
})

downloadRequest.interceptors.request.use((config) => {
  const store = useUserStore()
  if (store.token) {
    config.headers.Authorization = `Bearer ${store.token}`
  }
  return config
})

downloadRequest.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const store = useUserStore()
      store.logout()
      // dynamic import to avoid circular dep
      import('../router').then(({ default: router }) => router.push('/login'))
    }
    return Promise.reject(error)
  }
)

export default downloadRequest
