import React from 'react';
import { Box } from '@mui/material';
import Header from '../components/Header';
import Sidebar from '../components/Sidebar';

const MainLayout = ({ children }) => {
  return (
    <Box sx={{ display: 'flex', bgcolor: 'grey.50', minHeight: '100vh' }}>
      <Header />
      <Sidebar />
      <Box 
        component="main" 
        sx={{ 
          flexGrow: 1, 
          p: 3, 
          mt: '64px' // AppBar height
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default MainLayout; 