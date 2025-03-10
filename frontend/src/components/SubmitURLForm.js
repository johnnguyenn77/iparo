import React, { useState } from 'react';
import '../styles/SubmitURLForm.css';

function SubmitURLForm({ onSubmit }) {
  const [url, setUrl] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(url);
  };

  return (
    <form className="submit-url-form" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Enter a URL to track"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />
      <button type="submit">Submit</button>
    </form>
  );
}

export default SubmitURLForm;