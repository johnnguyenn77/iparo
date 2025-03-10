import React, { useState } from 'react';
import SubmitURLForm from '../components/SubmitURLForm';
import { submitNewURL } from '../services/archiveService';
import '../styles/SubmitNewURLPage.css';

function SubmitNewURLPage() {
  const handleSubmit = (url) => {
    submitNewURL(url).then(response => {
      console.log('URL submitted:', response);
    });
  };

  return (
    <div className="submit-new-url-page">
      <h1>Track a New Website</h1>
      <SubmitURLForm onSubmit={handleSubmit} />
    </div>
  );
}

export default SubmitNewURLPage;