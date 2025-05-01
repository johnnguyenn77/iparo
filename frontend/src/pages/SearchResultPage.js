import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import {
  Box, Container, Typography, Paper, List, ListItem,
  ListItemButton, ListItemText, Divider, CircularProgress,
  Button, Breadcrumbs, Link as MuiLink
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { fetchSnapshotsByUrl } from '../services/archiveService';

export default function SearchResultsPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [snapshots, setSnapshots] = useState([]);
  const [error, setError] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();
  const searchedUrl = new URLSearchParams(location.search).get('url');

  useEffect(() => {
    if (!searchedUrl) { navigate('/'); return; }
    (async () => {
      try {
        setIsLoading(true);
        const data = await fetchSnapshotsByUrl(searchedUrl);
        setSnapshots(data);
        setError(null);
      } catch (err) {
        console.error(err);
        setError('Failed to load snapshot data.');
      } finally {
        setIsLoading(false);
      }
    })();
  }, [searchedUrl, navigate]);

  const formatDate = (s) =>
    new Date(s).toLocaleDateString(undefined, {
      year:'numeric',month:'long',day:'numeric',
      hour:'2-digit',minute:'2-digit'
    });

  return (
    <Box sx={{ py: 4 }}>
      <Container maxWidth="md">
        <Breadcrumbs sx={{ mb: 3 }}>
          <MuiLink component={Link} to="/" color="inherit">Home</MuiLink>
          <Typography color="text.primary">Search Results</Typography>
        </Breadcrumbs>

        <Paper sx={{ p:4, borderRadius:2 }}>
          <Typography variant="h4" gutterBottom>Archive Results</Typography>
          <Box sx={{ display:'flex', alignItems:'center', mb:2 }}>
            <SearchIcon color="secondary" sx={{ mr:1 }} />
            <Typography>{searchedUrl}</Typography>
          </Box>

          {isLoading ? (
            <Box sx={{ textAlign:'center', my:4 }}>
              <CircularProgress />
            </Box>
          ) : error ? (
            <Typography color="error">{error}</Typography>
          ) : snapshots.length === 0 ? (
            <Typography>No archived versions found.</Typography>
          ) : (
            <List>
              {snapshots.map((snap, i) => (
                <React.Fragment key={snap.id}>
                  <ListItem disablePadding>
                    <ListItemButton component={Link} to={`/view/${snap.id}`}>
                      <ListItemText
                        primary={formatDate(snap.timestamp)}
                        secondary={`ID: ${snap.id}`}
                      />
                    </ListItemButton>
                  </ListItem>
                  {i < snapshots.length-1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          )}
        </Paper>
      </Container>
    </Box>
  );
}