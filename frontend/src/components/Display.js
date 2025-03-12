import React from 'react';
import '../styles/Display.css';

function Display({ snapshot }) {
  if (!snapshot) {
    return <div>No snapshot data available.</div>;
  }

  return (
    <div className="display">
      <h2>Archived Webpage</h2>
      <iframe
        title="Archived Webpage"
        srcDoc={snapshot.content} //Render the archived webpage content
        style={{ width: '100%', height: '80vh', border: 'none' }}
      />
    </div>
  );
}

export default Display;