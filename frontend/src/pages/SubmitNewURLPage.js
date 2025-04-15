import React from 'react';
import { Box, Typography, Button, Paper, Container, Grid } from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { Link } from 'react-router-dom';
import '../styles/SubmitNewURLPage.css';

function SubmitNewURLPage() {
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
            Feature Not Available
          </Typography>
          
          <Typography 
            variant="h6" 
            color="text.secondary"
            sx={{ mb: 4 }}
          >
            The tracking of new webpages is not currently supported in this version.
          </Typography>
          
          <Box sx={{ mb: 4 }}>
            <Typography variant="body1" sx={{ mb: 3 }}>
              This feature has been temporarily removed. Please check back later for updates.
            </Typography>
          </Box>
          
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