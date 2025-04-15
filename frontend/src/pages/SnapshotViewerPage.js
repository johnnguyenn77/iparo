import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { 
  Box, Container, Typography, Paper, CircularProgress,
  Button, Breadcrumbs, Link as MuiLink, IconButton, 
  Tooltip, Divider, Grid, Alert
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import HistoryIcon from '@mui/icons-material/History';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import ShareIcon from '@mui/icons-material/Share';
import { fetchSnapshotById, initReconstructive } from '../services/archiveService';

function SnapshotViewerPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [snapshot, setSnapshot] = useState(null);
  const [error, setError] = useState(null);
  const [reconstructiveReady, setReconstructiveReady] = useState(false);
  const { id } = useParams();
  const navigate = useNavigate();
  const iframeRef = useRef(null);
  
useEffect(() => {
    const setupReconstructive = async () => {
      try {
        await initReconstructive();
        setReconstructiveReady(true);
      } catch (err) {
        console.error('Failed to initialize Reconstructive:', err);
        setError('Failed to initialize archive viewer. Please try again later.');
      }
    };
    
    setupReconstructive();
  }, []);
  
  useEffect(() => {
    const loadSnapshot = async () => {
      try {
        setIsLoading(true);
        const data = await fetchSnapshotById(id);
        setSnapshot(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching snapshot:', err);
        setError('Failed to load the archived version. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };
    
    loadSnapshot();
  }, [id]);
  
  const formatDate = (dateString) => {
    const options = { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, options);
  };
  
  return (
    <Box sx={{ py: 4 }}>
      <Container maxWidth="lg">
        <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 3 }}>
          <MuiLink component={Link} to="/" underline="hover" color="inherit">
            Home
          </MuiLink>
          <MuiLink component={Link} to="/results" underline="hover" color="inherit">
            Search Results
          </MuiLink>
          <Typography color="text.primary">Archived Page</Typography>
        </Breadcrumbs>
        
        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Paper elevation={3} sx={{ p: 4, borderRadius: 2, textAlign: 'center' }}>
            <Typography color="error" variant="h6" gutterBottom>
              {error}
            </Typography>
            <Button 
              component={Link} 
              to="/"
              variant="contained" 
              startIcon={<ArrowBackIcon />}
              sx={{ mt: 2 }}
            >
              Back to Home
            </Button>
          </Paper>
        ) : (
          <>
            <Paper elevation={3} sx={{ p: 3, borderRadius: 2, mb: 3 }}>
              <Grid container spacing={2} alignItems="center">
                <Grid item xs={12} md={8}>
                  <Typography
                    variant="h5"
                    component="h1"
                    gutterBottom
                    sx={{ fontWeight: 'bold', color: 'primary.main' }}
                  >
                    {snapshot.title}
                  </Typography>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <CalendarTodayIcon color="secondary" sx={{ mr: 1, fontSize: 20 }} />
                    <Typography variant="subtitle1" color="text.secondary">
                      Archived on: {formatDate(snapshot.timestamp)}
                    </Typography>
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2, wordBreak: 'break-all' }}>
                    Original URL: {snapshot.url}
                  </Typography>
                </Grid>
                
                <Grid item xs={12} md={4} sx={{ display: 'flex', justifyContent: { xs: 'flex-start', md: 'flex-end' } }}>
                  <Tooltip title="View all versions">
                    <Button
                      component={Link}
                      to={`/results?url=${encodeURIComponent(snapshot.url)}`}
                      startIcon={<HistoryIcon />}
                      sx={{ mr: 1 }}
                    >
                      All Versions
                    </Button>
                  </Tooltip>
                  
                  <Tooltip title="Visit current live page">
                    <IconButton 
                      component="a"
                      href={snapshot.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      color="primary"
                    >
                      <OpenInNewIcon />
                    </IconButton>
                  </Tooltip>
                  
                  <Tooltip title="Share this archive">
                    <IconButton
                      onClick={() => {
                        navigator.clipboard.writeText(window.location.href);
                        alert('Link copied to clipboard!');
                      }}
                      color="primary"
                    >
                      <ShareIcon />
                    </IconButton>
                  </Tooltip>
                </Grid>
              </Grid>
              
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                Archived snapshot ID: {snapshot.id}
              </Typography>
              
              <Button
                component={Link}
                to={-1}
                startIcon={<ArrowBackIcon />}
                sx={{ 
                  textTransform: 'none',
                  fontWeight: 'medium',
                  '&:hover': {
                    transform: 'translateX(-4px)',
                    transition: 'transform 0.2s ease-in-out'
                  }
                }}
              >
                Back to Results
              </Button>
            </Paper>
            
            <Alert severity="info" sx={{ mb: 3 }}>
              This is a demonstration of how archived content would appear. In a production environment, 
              Reconstructive would render the actual archived webpage with all its original styling and resources.
            </Alert>
            
            <Paper 
              elevation={3} 
              sx={{ 
                borderRadius: 2,
                overflow: 'hidden',
                height: '70vh',
                minHeight: '400px'
              }}
            >
              <Box 
                sx={{ 
                  height: '100%',
                  position: 'relative'
                }}
              >
                {/* 
                  In a real implementation with Reconstructive:
                    The iframe would load the memento URL
                    Reconstructive would rewrite all resource URLs to point to archived versions
                */}
                {reconstructiveReady ? (
                  <iframe
                    ref={iframeRef}
                    // In a real implementation, this would be a URL that Reconstructive intercepts
                    srcDoc={snapshot.htmlContent}
                    title={`Archived version of ${snapshot.url}`}
                    style={{ 
                      width: '100%', 
                      height: '100%',
                      border: 'none'
                    }}
                  />
                ) : (
                  <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                    <CircularProgress />
                    <Typography sx={{ ml: 2 }}>
                      Initializing archive viewer...
                    </Typography>
                  </Box>
                )}
              </Box>
            </Paper>
          </>
        )}
      </Container>
    </Box>
  );
}

export default SnapshotViewerPage;