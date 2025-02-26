import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import SnapshotList from '../components/SnapshotList';
import { fetchSnapshots } from '../services/archiveService';
import '../styles/HistoryPage.css';

function HistoryPage() {
  const [snapshots, setSnapshots] = useState([]);

  useEffect(() => {
    fetchSnapshots().then(data => setSnapshots(data));
  }, []);

  return (
    <div className="history-page">
      <Sidebar />
      <SnapshotList snapshots={snapshots} />
    </div>
  );
}

export default HistoryPage;