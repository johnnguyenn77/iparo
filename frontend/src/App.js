import React, { useMemo, useState } from 'react';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { ColorModeContext, createThemeWithMode } from './theme';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import HomePage from './pages/HomePage';
import DateLookupPage from './pages/DateLookupPage';
import SearchResultsPage from './pages/SearchResultPage';
import DateLookupResultsPage from './pages/DateLookupResultsPage';
import SnapshotViewerPage from './pages/SnapshotViewerPage';
import NotFoundPage from './pages/NotFoundPage';
import { initReconstructive } from './services/archiveService';

initReconstructive()
  .then(() => console.log('SW registered'))
  .catch(console.error);

function App() {
  const [mode, setMode] = useState('light');
  
  const colorMode = useMemo(
    () => ({
      toggleColorMode: () => {
        setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
      },
    }),
    [],
  );

  const theme = useMemo(() => createThemeWithMode(mode), [mode]);

  return (
    <ColorModeContext.Provider value={colorMode}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
            <Header />
            <Box sx={{ display: 'flex', flexGrow: 1 }}>
              <Sidebar />
              <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
                <Routes>
                  <Route path="/" element={<HomePage />} />
                  <Route path="/date-lookup" element={<DateLookupPage />} />
                  <Route path="/results" element={<SearchResultsPage />} /> 
                  <Route path="/date-results" element={<DateLookupResultsPage />} /> 
                  <Route path="/view/:id" element={<SnapshotViewerPage />} />
                  <Route path="*" element={<NotFoundPage />} />
                </Routes>
              </Box>
            </Box>
          </Box>
        </Router>
      </ThemeProvider>
    </ColorModeContext.Provider>
  );
}

export default App;