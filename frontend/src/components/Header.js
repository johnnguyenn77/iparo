import React from 'react';
import '../styles/Header.css';

function Header() {
  return (
    <header className="header">
      <h1>IPARO System</h1>
      <nav>
        <ul>
          <li><a href="/">Home</a></li>
          <li><a href="/iparo">IPARO</a></li>
          <li><a href="/link-strategy">Link Strategy</a></li>
        </ul>
      </nav>
    </header>
  );
}

export default Header;