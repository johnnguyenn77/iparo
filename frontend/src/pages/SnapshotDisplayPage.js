import React, { useState, useEffect } from 'react';
import Display from '../components/Display';
// import { fetchWARCSnapshot } from '../services/warcService';
import { Box, Typography, Paper, Container } from '@mui/material';
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
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: '100%',
        height: '100%',
        backgroundColor: '#f5f5f5',
      }}
    >
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Paper
          elevation={3}
          sx={{
            p: 4,
            borderRadius: 2,
            backgroundColor: '#ffffff',
            textAlign: 'center',
          }}
        >
          <Typography
            variant="h3"
            component="h1"
            gutterBottom
            sx={{ fontWeight: 'bold', color: 'primary.main', mb: 4 }}
          >
            Snapshot Display
          </Typography>
          
          <Box
            sx={{
              width: '100%',
              height: '60vh',
              backgroundColor: '#e0e0e0',
              borderRadius: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Typography variant="h6" color="text.secondary">
              Archived website content will be displayed here.
            </Typography>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
}

export default SnapshotDisplay;