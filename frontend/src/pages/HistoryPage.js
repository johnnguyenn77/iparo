import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Container, Grid } from '@mui/material';
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
    <Box
      sx={{
        display: 'flex',
        width: '100%',
        height: '100%',
        backgroundColor: '#f5f5f5',
      }}
    >
      <Sidebar />
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Paper
          elevation={3}
          sx={{
            p: 4,
            borderRadius: 2,
            backgroundColor: '#ffffff',
          }}
        >
          <Typography
            variant="h3"
            component="h1"
            gutterBottom
            sx={{ fontWeight: 'bold', color: 'primary.main', mb: 4 }}
          >
            History
          </Typography>
          <SnapshotList snapshots={snapshots} />
        </Paper>
      </Container>
    </Box>
  );
}

export default HistoryPage;