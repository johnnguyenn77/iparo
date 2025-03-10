import React, { useState } from 'react';
import Sidebar from '../components/Sidebar';
import DatePicker from '../components/DatePicker';
import SnapshotList from '../components/SnapshotList';
import { fetchClosestSnapshots } from '../services/archiveService';
import '../styles/DateLookupPage.css';

function DateLookupPage() {
  const [snapshots, setSnapshots] = useState([]);

  const handleDateSelect = (date) => {
    fetchClosestSnapshots(date).then(data => setSnapshots(data));
  };

  return (
    <div className="date-lookup-page">
      <Sidebar />
      <DatePicker onDateSelect={handleDateSelect} />
      <SnapshotList snapshots={snapshots} />
    </div>
  );
}

export default DateLookupPage;