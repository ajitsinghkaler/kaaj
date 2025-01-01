import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
} from '@mui/material';
import axios from 'axios';

interface Business {
  name: string;
  filing_number: string;
  status: string;
  filing_date: string;
  state_of_formation: string;
  principal_address: string;
  registered_agent_name: string;
  officers: Array<{
    name: string;
    title: string;
    address: string;
  }>;
  filing_history: Array<{
    filing_type: string;
    filing_date: string;
    effective_date: string;
  }>;
}

const SearchPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState<Business[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      setError('Please enter a business name');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await axios.get(`http://localhost:8000/search/${encodeURIComponent(searchTerm)}`);
      setResults(Array.isArray(response.data.data) ? response.data.data : [response.data.data]);
    } catch (err) {
      setError('Error searching for business. Please try again.');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom align="center">
        Florida Business Search
      </Typography>

      <Box sx={{ display: 'flex', gap: 2, mb: 4 }}>
        <TextField
          fullWidth
          label="Enter Business Name"
          variant="outlined"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <Button
          variant="contained"
          onClick={handleSearch}
          disabled={loading}
          sx={{ minWidth: 120 }}
        >
          {loading ? <CircularProgress size={24} /> : 'Search'}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {results.length > 0 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Business Name</TableCell>
                <TableCell>Filing Number</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Filing Date</TableCell>
                <TableCell>State</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {results.map((business, index) => (
                <TableRow key={index}>
                  <TableCell>{business.name}</TableCell>
                  <TableCell>{business.filing_number}</TableCell>
                  <TableCell>{business.status}</TableCell>
                  <TableCell>{business.filing_date}</TableCell>
                  <TableCell>{business.state_of_formation}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {results.length > 0 && (
        <Box sx={{ mt: 4 }}>
          {results.map((business, index) => (
            <Paper key={index} sx={{ p: 3, mb: 2 }}>
              <Typography variant="h6" gutterBottom>
                Detailed Information
              </Typography>
              
              <Typography variant="subtitle1" gutterBottom>
                Principal Address: {business.principal_address}
              </Typography>
              
              <Typography variant="subtitle1" gutterBottom>
                Registered Agent: {business.registered_agent_name}
              </Typography>

              {business.officers && business.officers.length > 0 && (
                <>
                  <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
                    Officers
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Name</TableCell>
                          <TableCell>Title</TableCell>
                          <TableCell>Address</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {business.officers.map((officer, idx) => (
                          <TableRow key={idx}>
                            <TableCell>{officer.name}</TableCell>
                            <TableCell>{officer.title}</TableCell>
                            <TableCell>{officer.address}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </>
              )}

              {business.filing_history && business.filing_history.length > 0 && (
                <>
                  <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
                    Filing History
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Filing Type</TableCell>
                          <TableCell>Filing Date</TableCell>
                          <TableCell>Effective Date</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {business.filing_history.map((filing, idx) => (
                          <TableRow key={idx}>
                            <TableCell>{filing.filing_type}</TableCell>
                            <TableCell>{filing.filing_date}</TableCell>
                            <TableCell>{filing.effective_date}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </>
              )}
            </Paper>
          ))}
        </Box>
      )}
    </Box>
  );
};

export default SearchPage; 