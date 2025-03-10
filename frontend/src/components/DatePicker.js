import React, { useState } from 'react';
import '../styles/DatePicker.css';

function DatePicker({ onDateSelect }) {
  const [date, setDate] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onDateSelect(date);
  };

  return (
    <form className="date-picker" onSubmit={handleSubmit}>
      <input
        type="datetime-local"
        value={date}
        onChange={(e) => setDate(e.target.value)}
      />
      <button type="submit">Find Closest Snapshot</button>
    </form>
  );
}

export default DatePicker;