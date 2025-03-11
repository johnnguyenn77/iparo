import React, { useState } from 'react';
import { Paper, InputBase, IconButton, Divider, Box } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

function SearchBar({ onSearch }) {
  const [url, setUrl] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (url.trim()) {
      onSearch(url.trim());
    }
  };

  return (
    <Paper
      component="form"
      onSubmit={handleSubmit}
      sx={{ 
        p: '2px 4px', 
        display: 'flex', 
        alignItems: 'center',
        width: '100%',
        border: '1px solid #e0e0e0',
        boxShadow: 1
      }}
    >
      <InputBase
        sx={{ ml: 1, flex: 1 }}
        placeholder="Enter URL to search archives"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        inputProps={{ 'aria-label': 'search web archives' }}
      />
      <Divider sx={{ height: 28, m: 0.5 }} orientation="vertical" />
      <IconButton 
        type="submit" 
        sx={{ p: '10px' }} 
        aria-label="search"
        color="primary"
      >
        <SearchIcon />
      </IconButton>
    </Paper>
  );
}

export default SearchBar;