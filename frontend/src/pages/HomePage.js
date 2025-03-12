import React from 'react';
import SearchBar from '../components/SearchBar';
import { Box, Typography, Button, Paper, Container, Grid, Divider } from '@mui/material';
import AddLinkIcon from '@mui/icons-material/AddLink';
import { Link } from 'react-router-dom';
import '../styles/HomePage.css';

function HomePage() {
  const handleSearch = (url) => {
    console.log('Searching for:', url);
  };

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: '100%',
        height: '100%'
      }}
    >
      <Container maxWidth="md">
        <Paper
          elevation={3}
          sx={{
            p: 4,
            borderRadius: 2,
            textAlign: 'center'
          }}
        >
          <Typography
            variant="h3"
            component="h1"
            gutterBottom
            sx={{ fontWeight: 'bold', color: 'primary.main' }}
          >
            Welcome to the IPARO Archive
          </Typography>
          
          <Typography 
            variant="h6" 
            color="text.secondary"
            sx={{ mb: 4 }}
          >
            Search for archived web pages or submit new URLs
          </Typography>
          
          <Box sx={{ mb: 4 }}>
            <SearchBar onSearch={handleSearch} />
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', my: 3 }}>
            <Divider sx={{ flexGrow: 1, maxWidth: 150 }} />
            <Typography 
              variant="h5" 
              sx={{ 
                px: 3, 
                fontWeight: 'bold',
                color: 'text.secondary'
              }}
            >
              OR
            </Typography>
            <Divider sx={{ flexGrow: 1, maxWidth: 150 }} />
          </Box>
          
          <Grid container justifyContent="center" sx={{ mt: 3 }}>
            <Button
              variant="contained"
              size="large"
              color="primary"
              startIcon={<AddLinkIcon />}
              component={Link}
              to="/submit-new-url"
              sx={{
                py: 2,
                px: 4,
                borderRadius: 2,
                textTransform: 'none',
                fontSize: '1.2rem',
                fontWeight: 'bold',
                boxShadow: 4,
                color: '#ffffff !important', 
                '&:hover': {
                  boxShadow: 8,
                  transform: 'scale(1.03)',
                  transition: 'all 0.2s ease-in-out',
                  color: '#ffffff' 
                }
              }}
            >
              Submit a new URL to be tracked
            </Button>
          </Grid>
        </Paper>
      </Container>
    </Box>
  );
}

export default HomePage;