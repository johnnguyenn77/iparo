import React from 'react';
import { Box, Container, Typography, Button, Paper } from '@mui/material';
import { Link } from 'react-router-dom';
import HomeIcon from '@mui/icons-material/Home';
import SearchIcon from '@mui/icons-material/Search';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';

function NotFoundPage() {
  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: '100%',
        height: '100%',
        py: 4
      }}
    >
      <Container maxWidth="md">
      <Paper
        elevation={3}
        sx={{
          p: 4,
          borderRadius: 4,
          textAlign: 'center',
          background: 'linear-gradient(to bottom right, #f8f9fa, #ffffff)',
          border: '1px solid rgba(0,0,0,0.1)'
        }}
      >
          <Box sx={{ 
            width: 120,
            height: 120,
            borderRadius: '50%',
            backgroundColor: 'error.light',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            mb: 3
          }}>
          <ErrorOutlineIcon 
            color="error" 
            sx={{ 
              fontSize: 60,
              mb: 2
            }} 
          />
          </Box>
          
          <Typography
            variant="h3"
            component="h1"
            gutterBottom
            sx={{ fontWeight: 'bold', color: 'error.main' }}
          >
            404 - Page Not Found
          </Typography>
          
          <Typography 
            variant="h6" 
            color="text.secondary"
            sx={{ mb: 4 }}
          >
            The page you're looking for doesn't exist or has been moved.
          </Typography>
          
          <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, justifyContent: 'center', gap: 2 }}>
            <Button
              component={Link}
              to="/"
              variant="contained"
              size="large"
              startIcon={<HomeIcon />}
              sx={{
                py: 1.5,
                px: 3,
                borderRadius: 2,
                textTransform: 'none',
                fontSize: '1rem',
                fontWeight: 'bold',
              }}
            >
              Back to Home
            </Button>
            
            <Button
              component={Link}
              to="/date-lookup"
              variant="outlined"
              size="large"
              startIcon={<SearchIcon />}
              sx={{
                py: 1.5,
                px: 3,
                borderRadius: 2,
                textTransform: 'none',
                fontSize: '1rem',
                fontWeight: 'bold',
              }}
            >
              Search Archives
            </Button>
          </Box>
          
          <Typography 
            variant="body2" 
            color="text.secondary"
            sx={{ mt: 4 }}
          >
            If you believe this is an error, please contact support.
          </Typography>
        </Paper>
      </Container>
    </Box>
  );
}

export default NotFoundPage;