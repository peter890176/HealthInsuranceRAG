import React from 'react';
import { Paper, Typography, Box, Alert } from '@mui/material';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const RagAnswer = ({ answer, relevantArticles = [] }) => {
  // Determine response type based on articles
  const getResponseType = (relevantArticles) => {
    if (!relevantArticles || relevantArticles.length === 0) {
      return { type: 'no_articles', message: 'No articles found in the database' };
    }
    
    const maxSimilarity = Math.max(...relevantArticles.map(a => a.similarity_score || 0));
    const articleCount = relevantArticles.length;
    
    if (maxSimilarity < 0.3 && articleCount <= 3) {
      return { type: 'no_relevant', message: 'No highly relevant literature found' };
    } else if (maxSimilarity < 0.3) {
      return { type: 'low_relevance', message: `Found ${articleCount} articles with limited relevance (max: ${(maxSimilarity * 100).toFixed(1)}%)` };
    } else if (articleCount <= 3) {
      return { type: 'limited_articles', message: `Only ${articleCount} articles found (good relevance: ${(maxSimilarity * 100).toFixed(1)}%)` };
    }
    
    return { type: 'normal', message: null };
  };

  const responseInfo = getResponseType(relevantArticles);


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
      
      {/* Response type alert */}
      {responseInfo.message && (
        <Alert 
          severity={responseInfo.type === 'normal' ? 'info' : responseInfo.type === 'limited_articles' ? 'warning' : 'error'} 
          sx={{ mb: 2 }}
        >
          {responseInfo.message}
        </Alert>
      )}
      
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