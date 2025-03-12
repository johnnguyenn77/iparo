import React from 'react';
import { List, ListItem, ListItemText, Typography, Paper } from '@mui/material';
import { Link } from 'react-router-dom';
import '../styles/SnapshotList.css';

function SnapshotList({ snapshots }) {
  return (
    <Paper elevation={0} sx={{ p: 2, backgroundColor: 'transparent' }}>
      <List>
        {snapshots.map((snapshot, index) => (
          <ListItem
            key={index}
            component={Link}
            to={`/snapshot/${snapshot.id}`}
            sx={{
              mb: 1,
              borderRadius: 2,
              backgroundColor: '#ffffff',
              '&:hover': {
                backgroundColor: '#f5f5f5',
              },
            }}
          >
            <ListItemText
              primary={snapshot.timestamp}
              secondary={snapshot.url}
              primaryTypographyProps={{ fontWeight: 'bold' }}
            />
          </ListItem>
        ))}
      </List>
    </Paper>
  );
}

export default SnapshotList;