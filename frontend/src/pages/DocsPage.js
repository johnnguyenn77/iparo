import React from 'react';
import { 
  Box, Container, Typography, Paper, Accordion, 
  AccordionSummary, AccordionDetails, Divider, Link 
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import DescriptionIcon from '@mui/icons-material/Description';

function DocsPage() {
  const documentationSections = [
    {
      title: "Getting Started",
      content: "Detailed information about getting started with installation and setup of the IPARO system can be found in the README files on the repository via the links below.",
      links: [
        { text: "IPARO Repository", url: "https://github.com/johnnguyenn77/iparo"},
        { text: "Frontend Setup", url: "https://github.com/johnnguyenn77/iparo/blob/main/frontend/README.md" },
        { text: "Backend Setup", url: "https://github.com/johnnguyenn77/iparo/blob/main/backend/README.md" }
      ]
    },
  ];

  return (
    <Box sx={{ py: 4 }}>
      <Container maxWidth="md">
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 4 }}>
          <DescriptionIcon color="primary" sx={{ fontSize: 40, mr: 2 }} />
          <Typography variant="h3" component="h1">
            Documentation
          </Typography>
        </Box>
        
        <Typography variant="body1" paragraph sx={{ mb: 4 }}>
          Welcome to the IPARO Archive documentation. Here you'll find guides, references, 
          and best practices for using our web archiving system.
        </Typography>

        {documentationSections.map((section, index) => (
          <Paper key={index} elevation={2} sx={{ mb: 3, borderRadius: 2 }}>
            <Accordion defaultExpanded={index === 0}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h5" component="h2">
                  {section.title}
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography paragraph>{section.content}</Typography>
                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle2" gutterBottom>
                  Related Resources:
                </Typography>
                <Box component="ul" sx={{ pl: 2, listStyleType: 'none' }}>
                  {section.links.map((link, linkIndex) => (
                    <li key={linkIndex}>
                      <Link href={link.url} color="secondary">
                        • {link.text}
                      </Link>
                    </li>
                  ))}
                </Box>
              </AccordionDetails>
            </Accordion>
          </Paper>
        ))}
      </Container>
    </Box>
  );
}

export default DocsPage;