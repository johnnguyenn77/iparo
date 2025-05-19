import { createTheme } from '@mui/material/styles';
import React from 'react';

// Define your color palettes for both modes
const getDesignTokens = (mode) => ({
  palette: {
    mode,
    ...(mode === 'light'
      ? {
          // Light mode palette
          primary: {
            main: '#1e3c72',
            light: '#2a5298',
            dark: '#162a4a',
          },
          secondary: {
            main: '#f76c6c',
            light: '#ff9e9e',
            dark: '#c03d3d',
          },
          background: {
            default: '#f8f9fa',
            paper: '#ffffff',
          },
          text: {
            primary: '#121212',
            secondary: '#4a4a4a',
          },
          divider: 'rgba(0, 0, 0, 0.12)',
        }
      : {
          // Dark mode palette
          primary: {
            main: '#4d8bf0',
            light: '#7aa7f3',
            dark: '#3562b7',
          },
          secondary: {
            main: '#ff6b6b',
            light: '#ff8989',
            dark: '#e64a4a',
          },
          background: {
            default: '#121212',
            paper: '#1e1e1e',
          },
          text: {
            primary: '#ffffff',
            secondary: 'rgba(255, 255, 255, 0.7)',
          },
          divider: 'rgba(255, 255, 255, 0.12)',
        }),
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
      fontSize: '2.5rem',
    },
    h3: {
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundImage: mode === 'light' 
            ? 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)'
            : 'linear-gradient(135deg, #121212 0%, #1e1e1e 100%)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          transition: 'background-color 0.3s ease',
        },
      },
    },
  },
});

// Create a context for the color mode
export const ColorModeContext = React.createContext({
  toggleColorMode: () => {},
});

export const createThemeWithMode = (mode) => createTheme(getDesignTokens(mode));