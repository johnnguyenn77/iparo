import React from 'react';
import SearchBar from '../components/SearchBar';
import { Box, Typography, Button, Paper, Container, Grid, Divider } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import { Link, useNavigate } from 'react-router-dom';
import '../styles/HomePage.css';

function HomePage() {
  const navigate = useNavigate();
  
  const handleSearch = (url) => {
    console.log('Searching for:', url);
    navigate(`/results?url=${encodeURIComponent(url)}`);
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
            Search for archived web pages
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
        
          <Grid container spacing={2} justifyContent="center" sx={{ mt: 3 }}>
            <Grid item xs={12} sm={6}>
              <Button
                component={Link}
                to="/date-lookup"
                variant="contained"
                size="large"
                color="secondary"
                startIcon={<CalendarTodayIcon />}
                sx={{
                  py: 2,
                  px: 2,
                  width: '100%',
                  borderRadius: 2,
                  textTransform: 'none',
                  fontSize: '1.1rem',
                  fontWeight: 'bold',
                  boxShadow: 3,
                }}
              >
                Search by specific date
              </Button>
            </Grid>
          </Grid>
        </Paper>
      </Container>
    </Box>
  );
}

export default HomePage;