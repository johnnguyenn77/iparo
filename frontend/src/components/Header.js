import React, { useContext } from 'react';
import { 
  AppBar, Toolbar, Typography, Button, Box, 
  IconButton, useMediaQuery, useTheme 
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import StorageIcon from '@mui/icons-material/Storage';
import SearchIcon from '@mui/icons-material/Search';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import MenuIcon from '@mui/icons-material/Menu';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import { ColorModeContext } from '../theme';

function Header({ toggleSidebar }) {
  const theme = useTheme();
  const colorMode = useContext(ColorModeContext);
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  return (
    <AppBar position="sticky" elevation={0} sx={{ 
      zIndex: theme.zIndex.drawer + 1,
      background: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)',
      borderBottom: '1px solid rgba(255,255,255,0.1)'
    }}>
      <Toolbar sx={{ minHeight: 80 }}>
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
              fontWeight: 700,
              letterSpacing: 1.2,
              fontFamily: '"Roboto Condensed", sans-serif',
              color: '#ffffff',
              textShadow: '0 1px 2px rgba(0,0,0,0.3)'
            }}
          >
            IPARO Archive
          </Typography>
        </Box>
        
        <Box sx={{ flexGrow: 1 }} />
        
        {!isMobile && (
          <Box sx={{ display: 'flex' }}>
            <IconButton 
              onClick={colorMode.toggleColorMode}
              color="inherit"
              sx={{ ml: 1 }}
            >
              {theme.palette.mode === 'dark' ? (
                <Brightness7Icon />
              ) : (
                <Brightness4Icon />
              )}
            </IconButton>
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