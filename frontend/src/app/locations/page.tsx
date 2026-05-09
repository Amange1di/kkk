'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import {
  Box,
  Typography,
  Button,
  TextField,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  LocationOn,
} from '@mui/icons-material';
import { locationsApi } from '@/services/api';
import type { Location } from '@/services/api';
import { useTranslation } from 'react-i18next';

export default function LocationsPage() {
  const { t } = useTranslation();
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingLocation, setEditingLocation] = useState<Location | null>(null);
  const [formData, setFormData] = useState<Partial<Location>>({
    name: '',
    location_type: 'building',
    building: '',
    floor: '',
    room_number: '',
  });

  useEffect(() => {
    fetchLocations();
  }, []);

  const fetchLocations = async () => {
    try {
      const response = await locationsApi.getAll();
      setLocations(response.data.results || response.data);
    } catch {
      setError(t('error_loading_data'));
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (location?: Location) => {
    if (location) {
      setEditingLocation(location);
      setFormData(location);
    } else {
      setEditingLocation(null);
      setFormData({
        name: '',
        location_type: 'building',
        building: '',
        floor: '',
        room_number: '',
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingLocation(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingLocation) {
        await locationsApi.update(editingLocation.id, formData);
      } else {
        await locationsApi.create(formData);
      }
      handleCloseDialog();
      fetchLocations();
    } catch {
      setError(t('error_loading_data'));
    }
  };

  const handleDelete = async (id: number) => {
    if (confirm(t('confirm_delete'))) {
      try {
        await locationsApi.delete(id);
        fetchLocations();
      } catch {
        setError(t('error_loading_data'));
      }
    }
  };

  const typeColors: Record<string, string> = {
    building: 'primary',
    floor: 'info',
    room: 'success',
    office: 'warning',
    warehouse: 'error',
  };

  const typeLabels: Record<string, string> = {
    building: t('building'),
    floor: t('floor'),
    room: t('room_number'),
    office: t('office'),
    warehouse: t('warehouse'),
    other: t('type'),
  };

  return (
    <DashboardLayout>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">{t('locations')}</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          {t('add_location')}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>{t('name')}</TableCell>
              <TableCell>{t('type')}</TableCell>
              <TableCell>{t('building')}</TableCell>
              <TableCell>{t('floor')}</TableCell>
              <TableCell>{t('room_number')}</TableCell>
              <TableCell>{t('actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {locations.map((location) => (
              <TableRow key={location.id}>
                <TableCell>{location.name}</TableCell>
                <TableCell>
                  <Chip
                    label={typeLabels[location.location_type] || location.location_type}
                    color={typeColors[location.location_type] as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>{location.building || '-'}</TableCell>
                <TableCell>{location.floor || '-'}</TableCell>
                <TableCell>{location.room_number || '-'}</TableCell>
                <TableCell>
                  <Button
                    size="small"
                    startIcon={<EditIcon />}
                    onClick={() => handleOpenDialog(location)}
                  >
                    {t('edit')}
                  </Button>
                  <Button
                    size="small"
                    startIcon={<DeleteIcon />}
                    color="error"
                    onClick={() => handleDelete(location.id)}
                  >
                    {t('delete')}
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingLocation ? t('edit_location') : t('add_location')}
        </DialogTitle>
        <form onSubmit={handleSubmit}>
          <DialogContent>
            <TextField
              fullWidth
              label={t('name')}
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              margin="normal"
              required
            />
            <FormControl fullWidth margin="normal" required>
                <InputLabel>{t('type')}</InputLabel>
                <Select
                  value={formData.location_type}
                  label={t('type')}
                  onChange={(e) => setFormData({ ...formData, location_type: e.target.value })}
                >
                  <MenuItem value="building">{t('building')}</MenuItem>
                  <MenuItem value="floor">{t('floor')}</MenuItem>
                  <MenuItem value="room">{t('room_number')}</MenuItem>
                  <MenuItem value="office">{t('office')}</MenuItem>
                  <MenuItem value="warehouse">{t('warehouse')}</MenuItem>
                  <MenuItem value="other">{t('type')}</MenuItem>
                </Select>
              </FormControl>
            <TextField
              fullWidth
              label={t('building')}
              value={formData.building}
              onChange={(e) => setFormData({ ...formData, building: e.target.value })}
              margin="normal"
            />
            <TextField
              fullWidth
              label={t('floor')}
              value={formData.floor}
              onChange={(e) => setFormData({ ...formData, floor: e.target.value })}
              margin="normal"
            />
            <TextField
              fullWidth
              label={t('room_number')}
              value={formData.room_number}
              onChange={(e) => setFormData({ ...formData, room_number: e.target.value })}
              margin="normal"
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>{t('cancel')}</Button>
            <Button type="submit" variant="contained">
              {editingLocation ? t('save') : t('save')}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </DashboardLayout>
  );
}
