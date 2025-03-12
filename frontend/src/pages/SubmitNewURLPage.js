import React, { useState } from 'react';
import { Box, Typography, Button, Paper, Container, Grid, TextField } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { Link } from 'react-router-dom';
import { submitNewURL } from '../services/archiveService';
import '../styles/SubmitNewURLPage.css';

function SubmitNewURLPage() {
  const [url, setUrl] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!url.trim()) {
      setError('Please enter a valid URL');
      return;
    }

    setSubmitting(true);
    setError('');
    
    submitNewURL(url)
      .then(response => {
        console.log('URL submitted:', response);
        setSubmitted(true);
        setUrl('');
      })
      .catch(err => {
        console.error('Error submitting URL:', err);
        setError('Failed to submit URL. Please try again.');
      })
      .finally(() => {
        setSubmitting(false);
      });
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
            Track a New Website
          </Typography>
          
          <Typography 
            variant="h6" 
            color="text.secondary"
            sx={{ mb: 4 }}
          >
            Submit a URL to begin tracking changes to the webpage
          </Typography>
          
          {!submitted ? (
            <Box component="form" onSubmit={handleSubmit} sx={{ mb: 4 }}>
              <TextField
                label="Website URL"
                variant="outlined"
                fullWidth
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com"
                error={!!error}
                helperText={error}
                sx={{ mb: 3 }}
              />
              
              <Button
                variant="contained"
                size="large"
                color="primary"
                startIcon={<SendIcon />}
                type="submit"
                disabled={submitting}
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
                {submitting ? 'Submitting...' : 'Submit URL for Tracking'}
              </Button>
            </Box>
          ) : (
            <Box sx={{ mb: 4 }}>
              <Typography variant="h5" color="primary" sx={{ mb: 3 }}>
                URL successfully submitted!
              </Typography>
              
              <Typography variant="body1" sx={{ mb: 3 }}>
                We'll begin tracking changes to this website. You can view archived versions in your history.
              </Typography>
              
              <Button
                variant="outlined"
                onClick={() => setSubmitted(false)}
                sx={{ 
                  mr: 2,
                  py: 1,
                  px: 3,
                  borderRadius: 2,
                  textTransform: 'none',
                  fontWeight: 'bold',
                  '&:hover': {
                    boxShadow: 2,
                    transform: 'scale(1.02)',
                    transition: 'all 0.2s ease-in-out'
                  }
                }}
              >
                Submit Another URL
              </Button>
            </Box>
          )}
          
          <Grid container justifyContent="center" sx={{ mt: 3 }}>
            <Button
              component={Link}
              to="/"
              variant="text"
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
          </Grid>
        </Paper>
      </Container>
    </Box>
  );
}

export default SubmitNewURLPage;