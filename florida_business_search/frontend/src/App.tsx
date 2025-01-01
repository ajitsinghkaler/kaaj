import React from 'react';
import { Container, CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import SearchPage from './components/SearchPage'

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="lg">
        <SearchPage />
      </Container>
    </ThemeProvider>
  );
}

export default App; 