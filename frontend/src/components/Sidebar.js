import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/Sidebar.css';

function Sidebar() {
  return (
    <div className="sidebar">
      <ul>
        <li><Link to="/">Home</Link></li>
        <li><Link to="/history">All Versions</Link></li>
        <li><Link to="/date-lookup">Specific Version Lookup</Link></li>
      </ul>
    </div>
  );
}

export default Sidebar;