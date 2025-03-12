import React, { useState, useEffect } from 'react';
import Display from '../components/Display';
// import { fetchWARCSnapshot } from '../services/warcService';
import '../styles/SnapshotDisplayPage.css';

// function SnapshotDisplay({ match }) {
//   const [snapshot, setSnapshot] = useState(null);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState(null);

//   const snapshotId = match.params.id; // Get the snapshot ID from the URL

//   useEffect(() => {
//     // Fetch the WARC snapshot data
//     fetchWARCSnapshot(snapshotId)
//       .then((data) => {
//         setSnapshot(data);
//         setLoading(false);
//       })
//       .catch((err) => {
//         setError(err.message);
//         setLoading(false);
//       });
//   }, [snapshotId]);

//   if (loading) {
//     return <div>Loading...</div>;
//   }

//   if (error) {
//     return <div>Error: {error}</div>;
//   }

//   return (
//     <div className="snapshot-display">
//       <h1>Snapshot Display</h1>
//       <Display snapshot={snapshot} />
//     </div>
//   );
// }

function SnapshotDisplay() {
    return (
        <div className="snapshot-display">
          <h1>Snapshot Display</h1>
          <p> Temporarily blank for now</p>
        </div>
      );
}

export default SnapshotDisplay;