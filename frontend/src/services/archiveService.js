//Mock functions for now

export const fetchSnapshots = async () => {
    //Replace with actual data/logic later
    return [
      { id: 1, url: 'https://example.com', timestamp: '2023-10-01T12:00:00Z' },
      { id: 2, url: 'https://example.com', timestamp: '2023-10-02T12:00:00Z' },
    ];
  };
  
  export const fetchClosestSnapshots = async (date) => {
    //Replace with actual data/logic later
    return [
      { id: 1, url: 'https://example.com', timestamp: '2023-10-01T12:00:00Z' },
      { id: 2, url: 'https://example.com', timestamp: '2023-10-02T12:00:00Z' },
    ];
  };
  
  export const submitNewURL = async (url) => {
    //Replace with actual data/logic later
    return { success: true, message: 'URL submitted successfully' };
  };