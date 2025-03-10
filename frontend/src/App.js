import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import HomePage from './pages/HomePage';
import HistoryPage from './pages/HistoryPage';
import DateLookupPage from './pages/DateLookupPage';
import SubmitNewURLPage from './pages/SubmitNewURLPage';
import Header from './components/Header';
import Footer from './components/Footer';
import './styles/App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/date-lookup" element={<DateLookupPage />} />
          <Route path="/submit-new-url" element={<SubmitNewURLPage />} />
        </Routes>
        <Footer />
      </div>
    </Router>
  );
}

export default App;