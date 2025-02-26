import React from 'react';
import '../styles/SnapshotList.css';

function SnapshotList({ snapshots }) {
  return (
    <div className="snapshot-list">
      <h2>Snapshots</h2>
      <ul>
        {snapshots.map((snapshot, index) => (
          <li key={index}>
            <a href={`/snapshot/${snapshot.id}`}>{snapshot.timestamp}</a>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default SnapshotList;