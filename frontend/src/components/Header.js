import React from 'react';
import { 
  AppBar, Toolbar, Typography, Button, Box, 
  IconButton, useMediaQuery, useTheme 
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import StorageIcon from '@mui/icons-material/Storage';
import SearchIcon from '@mui/icons-material/Search';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import MenuIcon from '@mui/icons-material/Menu';

function Header({ toggleSidebar }) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  return (
    <AppBar position="sticky" elevation={2} sx={{ zIndex: theme.zIndex.drawer + 1 }}>
      <Toolbar>
        {isMobile && (
          <IconButton
            color="inherit"
            aria-label="open drawer"
            onClick={toggleSidebar}
            edge="start"
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
        )}
        
        <Box 
          component={RouterLink} 
          to="/" 
          sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            textDecoration: 'none', 
            color: 'inherit' 
          }}
        >
          <StorageIcon sx={{ mr: 1 }} />
          <Typography
            variant="h6"
            noWrap
            component="div"
            sx={{ 
              fontWeight: 'bold',
              display: { xs: isMobile ? 'none' : 'block', sm: 'block' }
            }}
          >
            IPARO Archive
          </Typography>
        </Box>
        
        <Box sx={{ flexGrow: 1 }} />
        
        {!isMobile && (
          <Box sx={{ display: 'flex' }}>
            <Button
              component={RouterLink}
              to="/"
              color="inherit"
              startIcon={<SearchIcon />}
              sx={{ mx: 1 }}
            >
              URL Search
            </Button>
            <Button
              component={RouterLink}
              to="/date-lookup"
              color="inherit"
              startIcon={<CalendarTodayIcon />}
              sx={{ mx: 1 }}
            >
              Date Search
            </Button>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
}

export default Header;