import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default {
  checkHealth() { return apiClient.get('/health'); },
  
  getAlbums() { return apiClient.get('/albums/'); },
  getAlbumDetails(id) { return apiClient.get(`/albums/${id}`); },
  createAlbum(data) { return apiClient.post('/albums/', data); },
  deleteAlbum(id) { return apiClient.delete(`/albums/${id}`); },

  getMedia(skip = 0, limit = 1000) { return apiClient.get(`/media/?skip=${skip}&limit=${limit}`); },
  getVaultMedia(skip = 0, limit = 1000) { return apiClient.get(`/media/vault?skip=${skip}&limit=${limit}`); },
  
  getMediaDetails(id) { return apiClient.get(`/media/${id}/details`); },

  uploadFiles(formData) {
    return apiClient.post('/media/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },

  setAlbum(ids, albumId) { 
    const payload = Array.isArray(ids) ? ids : [ids];
    return apiClient.put(`/media/bulk/album/${albumId}`, payload); 
  },

  scanLibrary() { return apiClient.post('/media/scan'); },

  getAuthStatus() { return apiClient.get('/auth/status'); },
  getSystemStats() { return apiClient.get('/system/stats'); },
  setupSecurity(mp, pin) { return apiClient.post('/auth/setup', { master_password: mp, pin: pin }); },
  login(pin) { return apiClient.post('/auth/login', { pin }); },
  changePin(masterPassword, newPin) { 
    return apiClient.post('/auth/change-pin', { master_password: masterPassword, new_pin: newPin }); 
  },
  
  sendHeartbeat() { return apiClient.post('/system/heartbeat'); },

  checkUpdates() { return apiClient.get('/system/updates/check'); },
  installUpdate() { return apiClient.post('/system/updates/install'); },
  restartApp() { return apiClient.post('/system/restart'); },

  encryptMedia(ids) { 
    const payload = Array.isArray(ids) ? ids : [ids];
    return apiClient.post('/media/bulk/encrypt', payload); 
  },
  decryptMedia(ids) { 
    const payload = Array.isArray(ids) ? ids : [ids];
    return apiClient.post('/media/bulk/decrypt', payload); 
  },
  deleteMedia(ids) { 
    const payload = Array.isArray(ids) ? ids : [ids];
    return apiClient.post('/media/bulk/delete', payload); 
  }
};