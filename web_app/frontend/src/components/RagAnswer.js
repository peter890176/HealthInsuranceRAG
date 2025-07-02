import React from 'react';
import { Paper, Typography, Box } from '@mui/material';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const RagAnswer = ({ answer, relevantArticles = [] }) => {


  // Process PMID links in text
  const processPmidLinks = (text) => {
    // Regex to match PMID format
    const pmidRegex = /PMID:\s*(\d+)/g;
    
    return text.replace(pmidRegex, (match, pmid) => {
      // Find corresponding article rank by PMID
      const article = relevantArticles.find(a => a.pmid === pmid);
      const rank = article ? article.rank : null;
      
      console.log(`Processing PMID: ${pmid}, found rank: ${rank}`); // Debug log
      
      if (rank) {
        return `[${match}](#article-${rank})`;
      }
      return match;
    });
  };

  // Handle PMID click events
  const handlePmidClick = (pmid, rank) => {
    console.log(`PMID clicked: ${pmid}, rank: ${rank}`); // Debug log
    const element = document.getElementById(`article-${rank}`);
    console.log(`Found element:`, element); // Debug log
    
    if (element) {
      // Smooth scroll to target element
      element.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
      });
      
      // Add highlight effect
      element.style.backgroundColor = '#fff3cd';
      element.style.transition = 'background-color 0.3s ease';
      
      // Remove highlight after 2 seconds
      setTimeout(() => {
        element.style.backgroundColor = '';
      }, 2000);
    } else {
      console.log(`Element with id 'article-${rank}' not found`); // Debug log
    }
  };

  // Custom link renderer for PMID links
  const customLinkRenderer = ({ href, children }) => {
    // Check if this is a PMID link (internal anchor)
    if (href && href.startsWith('#article-')) {
      const rank = href.replace('#article-', '');
      const pmid = children.toString().replace('PMID: ', '');
      
      return (
        <a 
          href={href} 
          className="pmid-link"
          onClick={(e) => {
            e.preventDefault();
            handlePmidClick(pmid, rank);
          }}
        >
          {children}
        </a>
      );
    }
    
    // Regular external links
    return (
      <a href={href} target="_blank" rel="noopener noreferrer">
        {children}
      </a>
    );
  };

  const processedAnswer = processPmidLinks(answer);
  console.log('Processed answer:', processedAnswer); // Debug log
  console.log('Relevant articles:', relevantArticles); // Debug log

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
        '& .pmid-link': { 
          color: 'primary.main', 
          textDecoration: 'underline',
          cursor: 'pointer',
          fontWeight: 'bold',
          '&:hover': {
            color: 'primary.dark',
            textDecoration: 'none'
          }
        }
      }}>
        <ReactMarkdown 
          remarkPlugins={[remarkGfm]}
          components={{
            a: customLinkRenderer
          }}
        >
          {processedAnswer}
        </ReactMarkdown>
      </Box>
    </Paper>
  );
};

export default RagAnswer; 