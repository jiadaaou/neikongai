import request from './request'

/**
 * 法律文档 API
 */

// 上传法律文档
export const uploadLaw = (formData) => {
  return request({
    url: '/admin/laws/upload',
    method: 'POST',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取法律列表
export const getLawsList = (params) => {
  return request({
    url: '/admin/laws',
    method: 'GET',
    params
  })
}

// 获取法律详情
export const getLawDetail = (id) => {
  return request({
    url: `/admin/laws/${id}`,
    method: 'GET'
  })
}

// 获取文档分块
export const getLawChunks = (id) => {
  return request({
    url: `/admin/laws/${id}/chunks`,
    method: 'GET'
  })
}

// 获取分块详情
export const getChunkDetail = (id) => {
  return request({
    url: `/admin/laws/chunks/${id}`,
    method: 'GET'
  })
}

// 删除法律文档
export const deleteLaw = (id) => {
  return request({
    url: `/admin/laws/${id}`,
    method: 'DELETE'
  })
}

// 获取处理日志
export const getLawLogs = (id) => {
  return request({
    url: `/admin/laws/${id}/logs`,
    method: 'GET'
  })
}

// 测试检索
export const testSearch = (data) => {
  return request({
    url: '/admin/laws/test-search',
    method: 'POST',
    data,
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

// 更新分块
export const updateChunk = (id, data) => {
  return request({
    url: `/admin/laws/chunks/${id}`,
    method: 'PUT',
    data,
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

// 删除分块
export const deleteChunk = (id) => {
  return request({
    url: `/admin/laws/chunks/${id}`,
    method: 'DELETE'
  })
}

// 重新处理文档
export const reprocessDocument = (id) => {
  return request({
    url: `/admin/laws/${id}/reprocess`,
    method: 'POST'
  })
}
