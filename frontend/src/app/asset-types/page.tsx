'use client';

import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Button,
  Container,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  FormControl,
  IconButton,
  InputLabel,
  MenuItem,
  Paper,
  TextField,
  Typography,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { assetTypesApi, AssetType } from '@/services/api';
import DashboardLayout from '@/components/DashboardLayout';

export default function AssetTypesPage() {
  const { t, i18n } = useTranslation();
  const [assetTypes, setAssetTypes] = useState<AssetType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingType, setEditingType] = useState<AssetType | null>(null);
  const [deletingType, setDeletingType] = useState<AssetType | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    description: '',
    is_active: true,
  });

  const fetchAssetTypes = async () => {
    try {
      setLoading(true);
      const response = await assetTypesApi.getAll();
      setAssetTypes(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load asset types');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssetTypes();
  }, []);

  const handleOpenDialog = (type?: AssetType) => {
    if (type) {
      setEditingType(type);
      setFormData({
        name: type.name,
        code: type.code,
        description: type.description || '',
        is_active: type.is_active,
      });
    } else {
      setEditingType(null);
      setFormData({
        name: '',
        code: '',
        description: '',
        is_active: true,
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingType(null);
    setDeletingType(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingType) {
        await assetTypesApi.update(editingType.id, formData);
      } else {
        await assetTypesApi.create(formData);
      }
      handleCloseDialog();
      fetchAssetTypes();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save asset type');
    }
  };

  const handleDelete = async () => {
    if (!deletingType) return;
    try {
      await assetTypesApi.delete(deletingType.id);
      handleCloseDialog();
      fetchAssetTypes();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete asset type');
    }
  };

  const filteredTypes = assetTypes.filter(
    (type) =>
      type.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      type.code.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <DashboardLayout>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            {t('asset_types')}
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            {t('add_asset_type_btn')}
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            placeholder={t('search_asset_types')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            size="small"
          />
        </Box>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : filteredTypes.length === 0 ? (
          <Typography align="center" color="text.secondary" sx={{ py: 4 }}>
            {t('no_asset_types_found')}
          </Typography>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>{t('asset_type_name')}</TableCell>
                  <TableCell>{t('asset_type_code')}</TableCell>
                  <TableCell>{t('asset_type_description')}</TableCell>
                  <TableCell>{t('assets_count')}</TableCell>
                  <TableCell>{t('status')}</TableCell>
                  <TableCell align="right">{t('actions')}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredTypes.map((type) => (
                  <TableRow key={type.id}>
                    <TableCell>{type.name}</TableCell>
                    <TableCell>{type.code}</TableCell>
                    <TableCell>{type.description || '-'}</TableCell>
                    <TableCell>{type.assets_count || 0}</TableCell>
                    <TableCell>
                      <Typography
                        color={type.is_active ? 'success.main' : 'error.main'}
                      >
                        {type.is_active ? t('active') : t('inactive')}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <IconButton
                        size="small"
                        color="primary"
                        onClick={() => handleOpenDialog(type)}
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => setDeletingType(type)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>

      {/* Add/Edit Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <form onSubmit={handleSubmit}>
          <DialogTitle>
            {editingType ? t('edit_asset_type') : t('add_asset_type')}
          </DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
              <TextField
                fullWidth
                label={t('asset_type_name')}
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
              <TextField
                fullWidth
                label={t('asset_type_code')}
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value.toLowerCase().replace(/\s+/g, '-') })}
                required
              />
              <TextField
                fullWidth
                label={t('asset_type_description')}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                multiline
                rows={3}
              />
              <FormControl fullWidth>
                <InputLabel>{t('status')}</InputLabel>
                <MenuItem
                  value="true"
                  selected={formData.is_active === true}
                  onClick={() => setFormData({ ...formData, is_active: true })}
                >
                  {t('active_status')}
                </MenuItem>
                <MenuItem
                  value="false"
                  selected={formData.is_active === false}
                  onClick={() => setFormData({ ...formData, is_active: false })}
                >
                  {t('inactive_status')}
                </MenuItem>
              </FormControl>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>{t('cancel_btn')}</Button>
            <Button type="submit" variant="contained">
              {editingType ? t('update_btn') : t('create_btn')}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!deletingType} onClose={handleCloseDialog}>
        <DialogTitle>{t('confirm_delete')}</DialogTitle>
        <DialogContent>
          <Typography>{t('confirm_delete_asset_type')}</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>{t('cancel_btn')}</Button>
          <Button onClick={handleDelete} variant="contained" color="error">
            {t('delete_btn')}
          </Button>
        </DialogActions>
      </Dialog>
      </Container>
    </DashboardLayout>
  );
}
