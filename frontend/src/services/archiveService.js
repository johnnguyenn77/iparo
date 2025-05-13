const API = path =>
  fetch(path, { credentials: 'same-origin' })
    .then(r => {
      if (!r.ok) throw new Error(r.statusText)
      return r.json()
    })

export const fetchSnapshotsByUrl = url =>
  API(`/api/snapshots?url=${encodeURIComponent(url)}`)
    .then(data => data.map(item => ({ id: item.cid, timestamp: item.timestamp })))

export const fetchSnapshotsByDate = (url, date, limit=3) =>
  API(`/api/snapshots/date?url=${encodeURIComponent(url)}` +
      `&date=${encodeURIComponent(date)}&limit=${limit}`)
    .then(data => data.map(item => ({ id: item.cid, timestamp: item.timestamp })))

export const fetchSnapshotById = id =>
  API(`/api/snapshot/${encodeURIComponent(id)}`)

export const fetchSnapshotContent = id =>
  fetch(`/api/archive/${encodeURIComponent(id)}/content`, { credentials: 'same-origin' })
    .then(r => {
      if (!r.ok) throw new Error(r.statusText)
      return r.text()
    })

export const initReconstructive = async () => {
  if (!('serviceWorker' in navigator))
    throw new Error('ServiceWorker unsupported')
  const reg = await navigator.serviceWorker.register(
    '/reconstructive-serviceworker.js',
    { scope: '/' }
  )
  await navigator.serviceWorker.ready
  return Boolean(reg.active)
}