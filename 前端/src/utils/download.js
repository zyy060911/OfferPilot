import axios from 'axios'
import { ElMessage } from 'element-plus'

/**
 * 文件下载专用 Axios 实例。
 * 与 src/utils/request.js 分离，因为下载端点的响应是二进制 Blob 而非 JSON Result<T>。
 *
 * 使用方式：
 *   import downloadRequest from '@/utils/download'
 *   const blob = await downloadRequest.get('/report/123/export', { params: { format: 'pdf' }, responseType: 'blob' })
 *   // 然后触发浏览器下载
 */
const downloadRequest = axios.create({
  baseURL: '/api',
  timeout: 120000 // 文件转换可能较慢，给 2 分钟
})

// 请求拦截器：注入 JWT
downloadRequest.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：区分成功（Blob）与错误（JSON）
downloadRequest.interceptors.response.use(
  (response) => {
    const contentType = response.headers['content-type'] || ''
    // 如果是 JSON（错误响应），解析并提示
    if (contentType.includes('application/json')) {
      return response.data.text().then(text => {
        try {
          const err = JSON.parse(text)
          ElMessage.error(err.message || '下载失败')
        } catch {
          ElMessage.error('下载失败')
        }
        return Promise.reject(new Error('服务器返回错误'))
      })
    }
    // 二进制文件，直接返回 blob
    return response.data
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
    } else {
      ElMessage.error(error.message || '下载失败，请检查网络')
    }
    return Promise.reject(error)
  }
)

export default downloadRequest
