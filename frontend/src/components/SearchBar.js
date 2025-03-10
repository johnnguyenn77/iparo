import React, { useState } from 'react';
import '../styles/SearchBar.css';

function SearchBar({ onSearch }) {
  const [url, setUrl] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(url);
  };

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Enter a URL to view archived material."
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />
      <button type="submit">Search</button>
    </form>
  );
}

export default SearchBar;