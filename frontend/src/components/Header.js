import React from 'react';
import { AppBar, Toolbar, Typography, Box } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import ArchiveIcon from '@mui/icons-material/Archive';

function Header() {
  return (
    <AppBar 
      position="fixed" 
      color="primary" 
      elevation={4}
      sx={{ 
        zIndex: (theme) => theme.zIndex.drawer + 1
      }}
    >
      <Toolbar>
        <Box 
          component={RouterLink} 
          to="/" 
          sx={{ 
            display: 'flex', 
            alignItems: 'center',
            textDecoration: 'none',
            color: 'inherit',
            '&:hover': {
              opacity: 0.9
            }
          }}
        >
          <ArchiveIcon sx={{ mr: 2, fontSize: 28 }} />
          <Typography
            variant="h6"
            component="div"
            sx={{
              fontFamily: 'monospace',
              fontWeight: 700,
              letterSpacing: '.2rem',
            }}
          >
            IPARO SYSTEM
          </Typography>
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default Header;