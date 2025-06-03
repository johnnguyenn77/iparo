import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link }             from 'react-router-dom';
import {
  Box, Container, Typography, Paper, CircularProgress,
  Button, Breadcrumbs, Link as MuiLink, Divider, Grid, Alert, IconButton
} from '@mui/material';
import ArrowBackIcon    from '@mui/icons-material/ArrowBack';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import HistoryIcon      from '@mui/icons-material/History';
import OpenInNewIcon    from '@mui/icons-material/OpenInNew';
import ShareIcon        from '@mui/icons-material/Share';
import { useTheme } from '@mui/material/styles';
import { fetchSnapshotById, initReconstructive } from '../services/archiveService';

export default function SnapshotViewerPage() {
  const { id } = useParams();
  const [loading, setLoading]   = useState(true);
  const [snapshot, setSnapshot] = useState(null);
  const [error, setError]       = useState(null);
  const [ready, setReady]       = useState(false);
  const iframeRef               = useRef(null);
  const theme = useTheme();

  useEffect(() => {
    initReconstructive()
      .then(() => setReady(true))
      .catch(() => setError('Failed to initialize archive viewer.'));
  }, []);

  useEffect(() => {
    fetchSnapshotById(id)
      .then(data => setSnapshot(data))
      .catch(() => setError('Failed to load archived version.'))
      .finally(() => setLoading(false));
  }, [id]);

  const formatDate = (s) =>
    new Date(s).toLocaleDateString(undefined, {
      year:'numeric',month:'long',day:'numeric',
      hour:'2-digit',minute:'2-digit'
    });
  const formatUTC = (s) =>
    new Date(s).toLocaleString(undefined, {
      timeZone: 'UTC',
      year:'numeric',month:'long',day:'numeric',
      hour:'2-digit',minute:'2-digit'
    });

  if (loading) return <CircularProgress sx={{ m: 4 }} />;
  if (error)   return <Alert severity="error">{error}</Alert>;

  return (
    <Box sx={{ py: 4 }}>
      <Container maxWidth="lg">
        <Breadcrumbs sx={{ mb: 3 }}>
          <MuiLink component={Link} to="/" color="inherit">Home</MuiLink>
          <MuiLink component={Link} to="/results" color="inherit">Search Results</MuiLink>
          <Typography color="text.primary">Archived Page</Typography>
        </Breadcrumbs>

        <Paper sx={{ p:3, borderRadius:2, mb:3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={8}>
              <Typography variant="h5" gutterBottom>
                {snapshot.title}
              </Typography>
              <Box sx={{ display:'flex', alignItems:'center' }}>
                <CalendarTodayIcon sx={{ mr:1 }} />
                <Typography>{formatDate(snapshot.timestamp)} (Local)</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                UTC: {formatUTC(snapshot.timestamp)}
              </Typography>
              <Divider sx={{ my:1 }} />
              <Typography variant="body2" sx={{ wordBreak:'break-all' }}>
                {snapshot.url}
              </Typography>
            </Grid>
            <Grid item xs={12} md={4} sx={{ textAlign:'right' }}>
              <Button component={Link} to={`/results?url=${encodeURIComponent(snapshot.url)}`} startIcon={<HistoryIcon />}>
                All Versions
              </Button>
              <IconButton href={snapshot.url} target="_blank"><OpenInNewIcon /></IconButton>
              <IconButton onClick={() => navigator.clipboard.writeText(window.location.href)}><ShareIcon /></IconButton>
            </Grid>
          </Grid>
          <Divider sx={{ my:2 }} />
          <Typography variant="caption">Snapshot ID: {snapshot.id}</Typography>
          <Button component={Link} to={-1} startIcon={<ArrowBackIcon />}>
            Back to Results
          </Button>
        </Paper>

        <Box sx={{
          position: 'relative',
          mb: 2,
          backgroundColor: theme.palette.warning.light,
          color: theme.palette.warning.contrastText,
          p: 2,
          borderRadius: 1,
          display: 'flex',
          alignItems: 'center',
          boxShadow: 1
        }}>
          <HistoryIcon sx={{ mr: 1.5, color: 'black'}} fill="black"/>
          <Typography variant="body2" color="black" sx={{ flexGrow: 1 }}>
            You are viewing an archived version of this page from {formatDate(snapshot.timestamp)}.
            Content may not function as originally intended.
          </Typography>
          <IconButton 
            size="small" 
            onClick={() => window.open(snapshot.url, '_blank')}
            sx={{ ml: 1, color: 'black'}}
          >
            <OpenInNewIcon fontSize="small" />
          </IconButton>
        </Box>

        <Paper sx={{ 
          borderRadius: 2, 
          overflow: 'hidden', 
          height: '70vh', 
          minHeight: 400,
          backgroundColor: 'transparent',
          backgroundImage: 'none'
        }}>
          <Box sx={{ 
            height: '100%', 
            position: 'relative',
            color: '#000 !important',
            bgcolor: 'transparent !important'
          }}>
            {ready ? (
              <iframe
                ref={iframeRef}
                src={snapshot.mementoUrl}
                title={`Archive of ${snapshot.url}`}
                style={{ 
                  width: '100%',
                  height: '100%',
                  border: 'none',
                  // Force light theme inside iframe:
                  backgroundColor: 'white',
                  colorScheme: 'light'
                }}
              />
            ) : (
              <Box sx={{ 
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                // Keep loader styling consistent
                backgroundColor: theme.palette.background.paper
              }}>
                <CircularProgress />
                <Typography sx={{ ml: 2 }}>Initializing archive viewer…</Typography>
              </Box>
            )}
          </Box>
        </Paper>
      </Container>
    </Box>
  );
}