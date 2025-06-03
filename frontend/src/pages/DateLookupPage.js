import React, { useState } from 'react';
import { 
  Box, Container, Typography, Paper, Button, 
  TextField, Breadcrumbs, Link as MuiLink
} from '@mui/material';
import { Link, useNavigate } from 'react-router-dom';
import SearchIcon from '@mui/icons-material/Search';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

function DateLookupPage() {
  const [url, setUrl] = useState('');
  const [selectedDate, setSelectedDate] = useState('');
  const [urlError, setUrlError] = useState('');
  const [dateError, setDateError] = useState('');
  const navigate = useNavigate();
  
  const validateUrl = (url) => {
    try {
      new URL(url);
      return true;
    } catch (e) {
      return false;
    }
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    setUrlError('');
    setDateError('');
    
    let hasError = false;
    
    if (!url.trim()) {
      setUrlError('URL is required');
      hasError = true;
    } else if (!validateUrl(url)) {
      setUrlError('Please enter a valid URL');
      hasError = true;
    }
    
    if (!selectedDate) {
      setDateError('Please select a date');
      hasError = true;
    }
    
    if (hasError) return;
    
    navigate(`/date-results?url=${encodeURIComponent(url)}&date=${encodeURIComponent(selectedDate)}`);
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
        <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 3 }}>
          <MuiLink component={Link} to="/" underline="hover" color="inherit">
            Home
          </MuiLink>
          <Typography color="text.primary">Date Lookup</Typography>
        </Breadcrumbs>
        
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
            Find Archived Version by Date
          </Typography>
          
          <Typography 
            variant="h6" 
            color="text.secondary"
            sx={{ mb: 4 }}
          >
            Enter a URL and select a date to find the closest archived version
          </Typography>
          
          <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Website URL"
              placeholder="https://example.com"
              variant="outlined"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              error={!!urlError}
              helperText={urlError}
              sx={{ mb: 3 }}
            />
            
            <TextField
              fullWidth
              label="Select Date"
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              InputLabelProps={{
                shrink: true,
              }}
              error={!!dateError}
              helperText={dateError || "Format: MM/DD/YYYY"}
              sx={{ mb: 3 }}
            />
            
            <Button
              type="submit"
              variant="contained"
              color="secondary"
              startIcon={<SearchIcon />}
              size="large"
              fullWidth
              sx={{
                py: 2,
                borderRadius: 2,
                textTransform: 'none',
                fontSize: '1.1rem',
                fontWeight: 'bold',
                boxShadow: 3,
                mt: 2
              }}
            >
              Find Archived Version
            </Button>
            
            <Button
              component={Link}
              to="/"
              startIcon={<ArrowBackIcon />}
              sx={{ 
                mt: 3, 
                display: 'inline-flex',
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
        </Paper>
      </Container>
    </Box>
  );
}

export default DateLookupPage;