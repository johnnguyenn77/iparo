import React, { useState } from 'react';
import { Box, Typography, Paper, Container, Grid } from '@mui/material';
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
            Date Lookup
          </Typography>
          <Grid container spacing={4}>
            <Grid item xs={12} md={4}>
              <DatePicker onDateSelect={handleDateSelect} />
            </Grid>
            <Grid item xs={12} md={8}>
              <SnapshotList snapshots={snapshots} />
            </Grid>
          </Grid>
        </Paper>
      </Container>
    </Box>
  );
}

export default DateLookupPage;