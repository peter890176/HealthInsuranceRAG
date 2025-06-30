import React from 'react';
import { Paper, Typography, Box } from '@mui/material';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const RagAnswer = ({ answer }) => {
  return (
    <Paper 
      sx={{ 
        p: 3, 
        bgcolor: 'primary.lightest',
        border: '1px solid',
        borderColor: 'primary.main',
        boxShadow: 3 
      }}
    >
      <Typography variant="h5" component="h2" color="primary.dark" sx={{ mb: 2 }}>
        AI-Generated Analysis
      </Typography>
      <Box sx={{
        '& p': { mb: 1.5 },
        '& h1, & h2, & h3': { mt: 2, mb: 1, borderBottom: '1px solid #ddd', pb: 0.5 },
        '& ul, & ol': { pl: 2.5, mb: 1.5 },
        '& a': { color: 'primary.dark', textDecoration: 'underline' },
      }}>
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{answer}</ReactMarkdown>
      </Box>
    </Paper>
  );
};

export default RagAnswer; 