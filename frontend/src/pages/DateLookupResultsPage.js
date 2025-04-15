import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { 
  Box, Container, Typography, Paper, List, ListItem, 
  ListItemButton, ListItemText, Divider, CircularProgress,
  Button, Breadcrumbs, Link as MuiLink, Alert
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import { fetchSnapshotsByDate } from '../services/archiveService';

function DateLookupResultsPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [snapshots, setSnapshots] = useState([]);
  const [error, setError] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();
  
  const queryParams = new URLSearchParams(location.search);
  const searchedUrl = queryParams.get('url');
  const searchedDate = queryParams.get('date');
  
useEffect(() => {
    if (!searchedUrl || !searchedDate) {
      navigate('/date-lookup');
      return;
    }
    
    const loadSnapshots = async () => {
      try {
        setIsLoading(true);
        const data = await fetchSnapshotsByDate(searchedUrl, searchedDate);
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
  }, [searchedUrl, searchedDate, navigate]);
  
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
  
  const formattedSearchDate = searchedDate ? formatDate(searchedDate) : '';
  
  return (
    <Box sx={{ py: 4 }}>
      <Container maxWidth="md">
        <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 3 }}>
          <MuiLink component={Link} to="/" underline="hover" color="inherit">
            Home
          </MuiLink>
          <MuiLink component={Link} to="/date-lookup" underline="hover" color="inherit">
            Date Lookup
          </MuiLink>
          <Typography color="text.primary">Results</Typography>
        </Breadcrumbs>
        
        <Paper elevation={3} sx={{ p: 4, borderRadius: 2 }}>
          <Typography
            variant="h4"
            component="h1"
            gutterBottom
            sx={{ fontWeight: 'bold', color: 'primary.main' }}
          >
            Date-Specific Archive Results
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <CalendarTodayIcon color="secondary" sx={{ mr: 1 }} />
            <Typography variant="h6" color="text.secondary">
              {formattedSearchDate}
            </Typography>
          </Box>
          
          <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 4, wordBreak: 'break-word' }}>
            URL: {searchedUrl}
          </Typography>
          
          {isLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
              <CircularProgress />
            </Box>
          ) : error ? (
            <Box sx={{ my: 3, textAlign: 'center' }}>
              <Typography color="error" gutterBottom>{error}</Typography>
              <Button 
                component={Link} 
                to="/date-lookup"
                variant="contained" 
                startIcon={<ArrowBackIcon />}
                sx={{ mt: 2 }}
              >
                Back to Date Lookup
              </Button>
            </Box>
          ) : snapshots.length === 0 ? (
            <Box sx={{ my: 3, textAlign: 'center' }}>
              <Typography variant="h6" gutterBottom>
                No archived versions found near this date.
              </Typography>
              <Typography color="text.secondary" paragraph>
                Try searching for a different date or URL.
              </Typography>
              <Button 
                component={Link} 
                to="/date-lookup"
                variant="contained" 
                startIcon={<ArrowBackIcon />}
                sx={{ mt: 2 }}
              >
                Back to Date Lookup
              </Button>
            </Box>
          ) : (
            <>
              <Alert severity="info" sx={{ mb: 3 }}>
                Showing the {snapshots.length} closest version{snapshots.length !== 1 ? 's' : ''} to your requested date.
              </Alert>
              
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
                          secondary={
                            <>
                              {snapshot.daysDifference === 0 
                                ? "Exact match!" 
                                : `${snapshot.daysDifference} day${snapshot.daysDifference !== 1 ? 's' : ''} ${
                                    new Date(snapshot.timestamp) > new Date(searchedDate) ? 'after' : 'before'
                                  } your selected date`}
                            </>
                          }
                          primaryTypographyProps={{
                            fontWeight: index === 0 ? 'bold' : 'medium',
                            color: index === 0 ? 'secondary.main' : 'primary.main'
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
                  to="/date-lookup"
                  startIcon={<ArrowBackIcon />}
                  sx={{ 
                    mr: 2,
                    textTransform: 'none',
                    fontWeight: 'bold',
                    '&:hover': {
                      transform: 'translateX(-4px)',
                      transition: 'transform 0.2s ease-in-out'
                    }
                  }}
                >
                  Back to Date Lookup
                </Button>
                
                <Button
                  component={Link}
                  to="/"
                  sx={{ 
                    textTransform: 'none',
                    fontWeight: 'bold'
                  }}
                >
                  Home
                </Button>
              </Box>
            </>
          )}
        </Paper>
      </Container>
    </Box>
  );
}

export default DateLookupResultsPage;