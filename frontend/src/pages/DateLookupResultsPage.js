import React, { useState, useEffect } from 'react'
import { useLocation, useNavigate, Link } from 'react-router-dom'
import {
  Box, Container, Typography, Paper, List, ListItem,
  ListItemButton, ListItemText, Divider, CircularProgress,
  Breadcrumbs, Link as MuiLink
} from '@mui/material'
import CalendarTodayIcon from '@mui/icons-material/CalendarToday'
import { fetchSnapshotsByDate } from '../services/archiveService'

export default function DateLookupResultsPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [snapshots, setSnapshots] = useState([])
  const [error, setError] = useState(null)
  const location = useLocation()
  const navigate = useNavigate()
  const params = new URLSearchParams(location.search)
  const url  = params.get('url')
  const date = params.get('date')

  useEffect(() => {
    if (!url || !date) { navigate('/'); return }
    ;(async () => {
      setIsLoading(true)
      try {
        const data = await fetchSnapshotsByDate(url, date)
        setSnapshots(data)
      } catch (e) {
        setError('Failed to load snapshot data.')
      } finally {
        setIsLoading(false)
      }
    })()
  }, [url, date, navigate])

  const formatDate = s =>
    new Date(s).toLocaleDateString(undefined, {
      year:'numeric', month:'long', day:'numeric',
      hour:'2-digit', minute:'2-digit'
    })

  return (
    <Box sx={{ py:4 }}>
      <Container maxWidth="md">
        <Breadcrumbs sx={{ mb:3 }}>
          <MuiLink component={Link} to="/" color="inherit">Home</MuiLink>
          <Typography color="text.primary">Date Lookup Results</Typography>
        </Breadcrumbs>

        <Paper sx={{ p:4, borderRadius:2 }}>
          <Box sx={{ display:'flex', alignItems:'center', mb:2 }}>
            <CalendarTodayIcon color="secondary" sx={{ mr:1 }}/>
            <Typography>{url} @ {date}</Typography>
          </Box>

          {isLoading ? (
            <Box sx={{ textAlign:'center', my:4 }}><CircularProgress/></Box>
          ) : error ? (
            <Typography color="error">{error}</Typography>
          ) : snapshots.length === 0 ? (
            <Typography>No snapshots around that date.</Typography>
          ) : (
            <List>
              {snapshots.map((snap, i) => (
                <React.Fragment key={snap.id}>
                  <ListItem disablePadding>
                    <ListItemButton component={Link} to={`/view/${snap.id}`}>
                      <ListItemText
                        primary={formatDate(snap.timestamp)}
                        secondary={`ID: ${snap.id}`}
                      />
                    </ListItemButton>
                  </ListItem>
                  {i < snapshots.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          )}
        </Paper>
      </Container>
    </Box>
  )
}