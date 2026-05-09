'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { useAuth } from '@/context/AuthContext';
import {
  Box,
  Typography,
  Button,
  TextField,
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
  Person,
} from '@mui/icons-material';
import axios from 'axios';
import { useTranslation } from 'react-i18next';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Создаём axios инстанс с токеном для запросов к users
const usersClient = axios.create({
  baseURL: `${API_URL}/accounts`,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Интерцептор для автоматического добавления токена
usersClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  department: string | null;
  is_active: boolean;
}

interface UserFormData {
  username: string;
  first_name: string;
  last_name: string;
  role: string;
  department: string;
  password?: string;
}

const ROLE_COLORS: Record<string, string> = {
  super_admin: 'error',
  inventory_manager: 'primary',
  staff: 'success',
  auditor: 'warning',
};

export default function UsersPage() {
  const { user: currentUser } = useAuth();
  const { t } = useTranslation();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [formData, setFormData] = useState<UserFormData>({
    username: '',
    first_name: '',
    last_name: '',
    role: 'staff',
    department: '',
    password: '',
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await usersClient.get('/users/');
      setUsers(response.data.results || response.data);
    } catch {
      setError(t('failed_to_load_users'));
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (user?: User) => {
    if (user) {
      setEditingUser(user);
      setFormData({
        username: user.username,
        first_name: user.first_name,
        last_name: user.last_name,
        role: user.role,
        department: user.department || '',
        password: '',
      });
    } else {
      setEditingUser(null);
      setFormData({
        username: '',
        first_name: '',
        last_name: '',
        role: 'staff',
        department: '',
        password: '',
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingUser(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingUser) {
        await usersClient.put(`/users/${editingUser.id}/`, formData);
      } else {
        await usersClient.post('/users/', formData);
      }
      handleCloseDialog();
      fetchUsers();
    } catch {
      setError(t('failed_to_save_user'));
    }
  };

  const handleDelete = async (id: number) => {
    if (confirm(t('confirm_delete_user'))) {
      try {
        await usersClient.delete(`/users/${id}/`);
        fetchUsers();
      } catch {
        setError(t('failed_to_delete_user'));
      }
    }
  };

  const canManageUsers = currentUser?.role === 'super_admin' || currentUser?.role === 'inventory_manager';

  if (!canManageUsers) {
    return (
      <DashboardLayout>
        <Alert severity="warning">{t('no_permission_manage_users')}</Alert>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">{t('users_management')}</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          {t('add_user_btn')}
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
              <TableCell>{t('username')}</TableCell>
              <TableCell>{t('name')}</TableCell>
              <TableCell>{t('role')}</TableCell>
              <TableCell>{t('department')}</TableCell>
              <TableCell>{t('status')}</TableCell>
              <TableCell>{t('actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id}>
                <TableCell>{user.username}</TableCell>
                <TableCell>{`${user.first_name} ${user.last_name}`}</TableCell>
                <TableCell>
                  <Chip
                    label={user.role.replace('_', ' ')}
                    color={ROLE_COLORS[user.role] as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>{user.department || '-'}</TableCell>
                <TableCell>
                  <Chip
                    label={user.is_active ? t('active_status') : t('inactive_status')}
                    color={user.is_active ? 'success' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Button
                    size="small"
                    startIcon={<EditIcon />}
                    onClick={() => handleOpenDialog(user)}
                  >
                    {t('edit_btn')}
                  </Button>
                  {user.id !== currentUser?.id && (
                    <Button
                      size="small"
                      startIcon={<DeleteIcon />}
                      color="error"
                      onClick={() => handleDelete(user.id)}
                    >
                      {t('delete_btn')}
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingUser ? t('edit_user_btn') : t('add_new_user')}
        </DialogTitle>
        <form onSubmit={handleSubmit}>
          <DialogContent>
            <TextField
              fullWidth
              label={t('username')}
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              margin="normal"
              required
              disabled={!!editingUser}
            />
            <TextField
              fullWidth
              label={t('password')}
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              margin="normal"
              required={!editingUser}
              helperText={editingUser ? t('password_helper') : ''}
            />
            <TextField
              fullWidth
              label={t('first_name')}
              value={formData.first_name}
              onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
              margin="normal"
            />
            <TextField
              fullWidth
              label={t('last_name')}
              value={formData.last_name}
              onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
              margin="normal"
            />
            <FormControl fullWidth margin="normal">
              <InputLabel>{t('role')}</InputLabel>
              <Select
                value={formData.role}
                label={t('role')}
                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
              >
                <MenuItem value="super_admin">{t('super_admin')}</MenuItem>
                <MenuItem value="inventory_manager">{t('inventory_manager')}</MenuItem>
                <MenuItem value="staff">{t('staff')}</MenuItem>
                <MenuItem value="auditor">{t('auditor')}</MenuItem>
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label={t('department')}
              value={formData.department}
              onChange={(e) => setFormData({ ...formData, department: e.target.value })}
              margin="normal"
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>{t('cancel_btn')}</Button>
            <Button type="submit" variant="contained">
              {editingUser ? t('update_btn') : t('create_btn')}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </DashboardLayout>
  );
}
