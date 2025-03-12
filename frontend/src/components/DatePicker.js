import React, { useState } from 'react';
import { TextField, Button, Box } from '@mui/material';
import '../styles/DatePicker.css';

function DatePicker({ onDateSelect }) {
  const [date, setDate] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onDateSelect(date);
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{
        display: 'flex',
        flexDirection: 'column',
        gap: 2,
      }}
    >
      <TextField
        type="datetime-local"
        label="Select Date and Time"
        value={date}
        onChange={(e) => setDate(e.target.value)}
        InputLabelProps={{ shrink: true }}
        fullWidth
      />
      <Button
        type="submit"
        variant="contained"
        color="primary"
        sx={{
          py: 1.5,
          borderRadius: 2,
          textTransform: 'none',
          fontWeight: 'bold',
        }}
      >
        Find Closest Snapshot
      </Button>
    </Box>
  );
}

export default DatePicker;