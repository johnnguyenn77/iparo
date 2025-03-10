import React from 'react';
import Sidebar from '../components/Sidebar';
import SearchBar from '../components/SearchBar';
import '../styles/HomePage.css';

function HomePage() {
  const handleSearch = (url) => {
    // Redirect to history page or fetch snapshots
    console.log('Searching for:', url);
  };

  return (
    <div className="home-page">
        <Sidebar />
        <div className="home-content">
            <h1>Welcome to the IPARO Archive</h1>
            <SearchBar onSearch={handleSearch} />
            <p>Or, <a href="/submit-new-url">submit a new URL to be tracked</a>.</p>
      </div>
    </div>
  );
}

export default HomePage;