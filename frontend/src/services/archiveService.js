const mockSnapshots = [
  {
    id: 'snapshot123',
    url: 'https://example.com',
    timestamp: '2023-04-15T08:30:00Z',
    title: 'Example Website - Home'
  },
  {
    id: 'snapshot456',
    url: 'https://example.com',
    timestamp: '2023-03-10T12:15:00Z',
    title: 'Example Website - Home'
  },
  {
    id: 'snapshot789',
    url: 'https://example.com',
    timestamp: '2023-02-22T16:45:00Z',
    title: 'Example Website - Home'
  },
  {
    id: 'snapshot101',
    url: 'https://example.org',
    timestamp: '2023-04-01T14:45:00Z',
    title: 'Example.org - Official Site'
  },
  {
    id: 'snapshot102',
    url: 'https://example.org',
    timestamp: '2023-01-15T10:20:00Z',
    title: 'Example.org - Official Site'
  }
];

/**
 * simulate API delay
 * @param {number} ms - milliseconds to delay
 * @returns {Promise<void>}
 */
const delay = (ms = 800) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * generate HTML content for a snapshot
 * @param {Object} snapshot - snapshot data
 * @returns {string} - HTML content
 */
const generateMockHtmlContent = (snapshot) => {
  const date = new Date(snapshot.timestamp).toLocaleDateString();
  return `
    <html>
      <head>
        <title>${snapshot.title}</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 20px; }
          h1 { color: #333; }
          p { line-height: 1.6; }
          .archived-banner { background-color: #f8f9fa; padding: 10px; border-bottom: 1px solid #ddd; text-align: center; }
        </style>
      </head>
      <body>
        <div class="archived-banner">
          This is an archived version of ${snapshot.url} from ${date}
        </div>
        <h1>${snapshot.title}</h1>
        <p>This is a placeholder for the actual archived content that would be displayed using Reconstructive.</p>
        <p>In a real implementation, this would show the website exactly as it appeared on ${date}.</p>
        <p>The archived URL is: ${snapshot.url}</p>
        <p>Snapshot ID: ${snapshot.id}</p>
      </body>
    </html>
  `;
};



/**
 * fetch all snapshots for a specific URL
 * @param {string} url - the URL to fetch snapshots for
 * @returns {Promise<Array>} - array of all snapshot objects for that URL
 */
export const fetchSnapshotsByUrl = async (url) => {
  await delay();
  return mockSnapshots
    .filter(snapshot => snapshot.url.toLowerCase() === url.toLowerCase())
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
};

/**
 * fetch the closest snapshots to a specific date for a URL
 * @param {string} url - the URL to fetch snapshots for
 * @param {string} date - the target date in ISO format
 * @param {number} limit - number of snapshots to return (default: 3)
 * @returns {Promise<Array>} - array of closest snapshot objects
 */
export const fetchSnapshotsByDate = async (url, date, limit = 3) => {
  await delay();
  
  const targetDate = new Date(date);
  const urlSnapshots = mockSnapshots.filter(snapshot => 
    snapshot.url.toLowerCase() === url.toLowerCase()
  );
  
  const snapshotsWithDifference = urlSnapshots.map(snapshot => ({
    ...snapshot,
    daysDifference: Math.abs(Math.round(
      (new Date(snapshot.timestamp) - targetDate) / (1000 * 60 * 60 * 24)
    ))
  }));
  
  return snapshotsWithDifference
    .sort((a, b) => a.daysDifference - b.daysDifference)
    .slice(0, limit);
};

/**
 * fetch a specific snapshot by ID
 * @param {string} id - the snapshot ID
 * @returns {Promise<Object>} - snapshot object with HTML content
 */
export const fetchSnapshotById = async (id) => {
  await delay(1000);
  
  const snapshot = mockSnapshots.find(s => s.id === id);
  
  if (!snapshot) {
    throw new Error('Snapshot not found');
  }
  
  return {
    ...snapshot,
    mementoUrl: `/api/archive/${id}/content`,
    htmlContent: generateMockHtmlContent(snapshot)
  };
};

/**
 * register the Reconstructive service worker
 * in a real implementation, this would register the actual Reconstructive service worker
 * @returns {Promise<boolean>} - success status
 */
export const initReconstructive = async () => {
  await delay(500);
  
  // leaving out cause not sure how it actually works
  // navigator.serviceWorker.register('/reconstructive-serviceworker.js')
  
  return true;
};