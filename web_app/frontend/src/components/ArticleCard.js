import React, { useState } from 'react';
import { Paper, Typography, Link, IconButton, Collapse, Box, Chip, ListItem } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';
import ArticleIcon from '@mui/icons-material/Article';
import PersonIcon from '@mui/icons-material/Person';

const ArticleCard = ({ article }) => {
  const [expanded, setExpanded] = useState(true);

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  // Format similarity score to percentage with 2 decimal places
  const formatSimilarityScore = (score) => {
    if (score === undefined || score === null) return 'N/A';
    return `${(score * 100).toFixed(2)}%`;
  };



  const getAuthors = (authors) => {
    if (!authors) return 'N/A';
    
    let authorList = [];
    
    // Handle different data formats
    if (Array.isArray(authors)) {
      // If it's already an array
      authorList = authors;
    } else if (typeof authors === 'string') {
      try {
        // Try to parse as JSON first
        authorList = JSON.parse(authors.replace(/'/g, '"'));
      } catch (e) {
        // If JSON parsing fails, treat as comma-separated string
        authorList = authors.split(',').map(author => author.trim());
      }
    } else {
      return 'N/A';
    }
    
    // Ensure authorList is an array
    if (!Array.isArray(authorList)) {
      return 'N/A';
    }
    
    // Filter out empty strings and limit to 2 authors
    const validAuthors = authorList.filter(author => author && author.trim() !== '');
    const displayAuthors = validAuthors.slice(0, 2);
    
    // Return formatted string
    if (displayAuthors.length === 0) {
      return 'N/A';
    } else if (validAuthors.length <= 2) {
      return displayAuthors.join(', ');
    } else {
      return displayAuthors.join(', ') + ' et al.';
    }
  };

  // Format date to show only year
  const formatDateToYear = (dateString) => {
    if (!dateString) return 'N/A';
    
    try {
      // Try to extract year from various date formats
      const date = new Date(dateString);
      if (!isNaN(date.getFullYear())) {
        return date.getFullYear().toString();
      }
      
      // If direct parsing fails, try to extract year from string
      const yearMatch = dateString.match(/\b(19|20)\d{2}\b/);
      if (yearMatch) {
        return yearMatch[0];
      }
      
      return 'N/A';
    } catch (e) {
      return 'N/A';
    }
  };

  // Debug logging
  React.useEffect(() => {
    console.log(`ArticleCard rendered with rank: ${article.rank}, pmid: ${article.pmid}, pub_date: ${article.pub_date}, similarity: ${article.similarity_score}`);
  }, [article.rank, article.pmid, article.pub_date, article.similarity_score]);

  return (
    <ListItem sx={{ display: 'block', p: 0, mb: 2 }}>
      <Paper 
        id={`article-${article.rank}`}
        sx={{ 
          p: 2.5, 
          ':hover': { boxShadow: 4 }, 
          transition: 'box-shadow 0.3s',
          scrollMarginTop: '20px' // Ensure proper margin when scrolling
        }}
      >
        <Box onClick={handleExpandClick} sx={{ cursor: 'pointer' }}>
          <Typography variant="h6" component="h3" sx={{ mb: 1 }}>
            {article.title || 'No Title Available'}
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, alignItems: 'center', mb: 1 }}>
            <Chip icon={<PersonIcon />} size="small" label={getAuthors(article.authors)} variant="outlined" />
            <Chip icon={<CalendarMonthIcon />} size="small" label={formatDateToYear(article.pub_date) || 'N/A'} variant="outlined" />
            <Chip icon={<ArticleIcon />} size="small" label={`PMID: ${article.pmid}`} variant="outlined" />
            <Chip 
              size="small" 
              label={`Similarity: ${formatSimilarityScore(article.similarity_score)}`} 
              variant="outlined"
            />
          </Box>
        </Box>
        <Collapse in={expanded} timeout="auto" unmountOnExit>
          <Typography variant="body2" sx={{ mt: 2, whiteSpace: 'pre-wrap', maxHeight: '200px', overflowY: 'auto', p: 1, bgcolor: 'grey.50', borderRadius: 1 }}>
            {article.abstract || 'No abstract available.'}
          </Typography>
        </Collapse>
        <Box sx={{ mt: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Link href={`https://pubmed.ncbi.nlm.nih.gov/${article.pmid}`} target="_blank" rel="noopener">
            View on PubMed
          </Link>
          <IconButton onClick={handleExpandClick} aria-label={expanded ? 'show less' : 'show more'}>
            {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Box>
      </Paper>
    </ListItem>
  );
};

export default ArticleCard; 