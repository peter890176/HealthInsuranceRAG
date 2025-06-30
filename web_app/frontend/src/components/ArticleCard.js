import React, { useState } from 'react';
import { Paper, Typography, Link, IconButton, Collapse, Box, Chip, ListItem } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';
import ArticleIcon from '@mui/icons-material/Article';
import PersonIcon from '@mui/icons-material/Person';

const ArticleCard = ({ article }) => {
  const [expanded, setExpanded] = useState(false);

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  const getAuthors = (authors) => {
    if (!authors) return 'N/A';
    try {
        const authorList = JSON.parse(authors.replace(/'/g, '"'));
        return authorList.slice(0, 3).join(', ') + (authorList.length > 3 ? ' et al.' : '');
    } catch (e) {
        return authors; // return raw string if parsing fails
    }
  };

  // Debug logging
  React.useEffect(() => {
    console.log(`ArticleCard rendered with rank: ${article.rank}, pmid: ${article.pmid}`);
  }, [article.rank, article.pmid]);

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
            <Chip icon={<CalendarMonthIcon />} size="small" label={article.publication_date || 'N/A'} variant="outlined" />
            <Chip icon={<ArticleIcon />} size="small" label={`PMID: ${article.pmid}`} variant="outlined" />
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