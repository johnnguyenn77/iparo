import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { 
  Box, Container, Typography, Paper, List, ListItem, 
  ListItemButton, ListItemText, Divider, CircularProgress,
  Button, Breadcrumbs, Link as MuiLink
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import SearchIcon from '@mui/icons-material/Search';
import { fetchSnapshotsByUrl } from '../services/archiveService';

function SearchResultsPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [snapshots, setSnapshots] = useState([]);
  const [error, setError] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();
  
  const queryParams = new URLSearchParams(location.search);
  const searchedUrl = queryParams.get('url');
  
  useEffect(() => {
    if (!searchedUrl) {
      navigate('/');
      return;
    }
    
    const loadSnapshots = async () => {
      try {
        setIsLoading(true);
        const data = await fetchSnapshotsByUrl(searchedUrl);
        setSnapshots(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching snapshots:', err);
        setError('Failed to load snapshot data. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };
    
    loadSnapshots();
  }, [searchedUrl, navigate]);
  
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
      <Container maxWidth="md">
        <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 3 }}>
          <MuiLink component={Link} to="/" underline="hover" color="inherit">
            Home
          </MuiLink>
          <Typography color="text.primary">Search Results</Typography>
        </Breadcrumbs>
        
        <Paper elevation={3} sx={{ p: 4, borderRadius: 2 }}>
          <Typography
            variant="h4"
            component="h1"
            gutterBottom
            sx={{ fontWeight: 'bold', color: 'primary.main' }}
          >
            Archive Results
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <SearchIcon color="secondary" sx={{ mr: 1 }} />
            <Typography variant="h6" color="text.secondary" sx={{ wordBreak: 'break-word' }}>
              {searchedUrl}
            </Typography>
          </Box>
          
          {isLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
              <CircularProgress />
            </Box>
          ) : error ? (
            <Box sx={{ my: 3, textAlign: 'center' }}>
              <Typography color="error" gutterBottom>{error}</Typography>
              <Button 
                component={Link} 
                to="/"
                variant="contained" 
                startIcon={<ArrowBackIcon />}
                sx={{ mt: 2 }}
              >
                Back to Home
              </Button>
            </Box>
          ) : snapshots.length === 0 ? (
            <Box sx={{ my: 3, textAlign: 'center' }}>
              <Typography variant="h6" gutterBottom>
                No archived versions found for this URL.
              </Typography>
              <Typography color="text.secondary" paragraph>
                Try searching for a different URL or check back later.
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
            </Box>
          ) : (
            <>
              <Typography variant="subtitle1" sx={{ mb: 3 }}>
                {snapshots.length} archived version{snapshots.length !== 1 ? 's' : ''} found
              </Typography>
              
              <List sx={{ width: '100%', bgcolor: 'background.paper', borderRadius: 1 }}>
                {snapshots.map((snapshot, index) => (
                  <React.Fragment key={snapshot.id}>
                    <ListItem disablePadding>
                      <ListItemButton 
                        component={Link} 
                        to={`/view/${snapshot.id}`}
                        sx={{
                          py: 2,
                          px: 3,
                          '&:hover': {
                            backgroundColor: 'rgba(0, 0, 0, 0.04)',
                          }
                        }}
                      >
                        <ListItemText 
                          primary={formatDate(snapshot.timestamp)} 
                          secondary={`Snapshot ID: ${snapshot.id}`}
                          primaryTypographyProps={{
                            fontWeight: 'medium',
                            color: 'primary.main'
                          }}
                        />
                      </ListItemButton>
                    </ListItem>
                    {index < snapshots.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
              
              <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
                <Button
                  component={Link}
                  to="/"
                  startIcon={<ArrowBackIcon />}
                  sx={{ 
                    textTransform: 'none',
                    fontWeight: 'bold',
                    '&:hover': {
                      transform: 'translateX(-4px)',
                      transition: 'transform 0.2s ease-in-out'
                    }
                  }}
                >
                  Back to Home
                </Button>
              </Box>
            </>
          )}
        </Paper>
      </Container>
    </Box>
  );
}

export default SearchResultsPage;