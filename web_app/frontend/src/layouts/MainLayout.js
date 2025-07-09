import React, { useState } from 'react';
import { Box, useTheme, useMediaQuery, IconButton } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import Header from '../components/Header';
import Sidebar from '../components/Sidebar';

const MainLayout = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <Box sx={{ display: 'flex', bgcolor: 'grey.50', minHeight: '100vh' }}>
      <Header onMenuClick={handleDrawerToggle} isMobile={isMobile} />
      <Sidebar 
        mobileOpen={mobileOpen} 
        onDrawerToggle={handleDrawerToggle}
        isMobile={isMobile}
      />
      <Box 
        component="main" 
        sx={{ 
          flexGrow: 1, 
          p: { xs: 2, sm: 3 }, // Responsive padding
          mt: { xs: '56px', sm: '64px' }, // Responsive margin top
          width: { xs: '100%', md: `calc(100% - 240px)` } // Responsive width
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default MainLayout; 