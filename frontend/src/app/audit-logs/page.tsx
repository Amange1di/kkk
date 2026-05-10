'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  ChipProps,
} from '@mui/material';
import {
  Assignment,
} from '@mui/icons-material';
import axios from 'axios';
import { useTranslation } from 'react-i18next';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://kkk-fwjw.onrender.com/api';

interface AuditLog {
  id: number;
  user: { username: string };
  action: string;
  model_name: string;
  object_name: string;
  ip_address: string;
  timestamp: string;
  changes: any;
}

const actionColors: Record<string, ChipProps['color']> = {
  create: 'success',
  update: 'info',
  delete: 'error',
  transfer: 'warning',
  scan: 'primary',
  checkout: 'info',
  checkin: 'success',
  report_damage: 'error',
  export: 'info',
  login: 'primary',
  logout: 'default',
};

export default function AuditLogsPage() {
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { t } = useTranslation();

  useEffect(() => {
    fetchAuditLogs();
  }, []);

  const fetchAuditLogs = async () => {
    try {
      const response = await axios.get(`${API_URL}/reports/audit-logs/`, {
        params: { ordering: '-timestamp' }
      });
      setAuditLogs(response.data.results || response.data);
    } catch {
      setError(t('error_loading_data'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Assignment sx={{ mr: 1, fontSize: 40 }} />
        <Typography variant="h4">{t('audit_logs')}</Typography>
      </Box>

      {error && (
        <Box sx={{ mb: 2 }}>
          <Typography color="error">{error}</Typography>
        </Box>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>{t('timestamp')}</TableCell>
              <TableCell>{t('user')}</TableCell>
              <TableCell>{t('action')}</TableCell>
              <TableCell>{t('model')}</TableCell>
              <TableCell>{t('object')}</TableCell>
              <TableCell>{t('ip_address')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {auditLogs.map((log) => (
              <TableRow key={log.id}>
                <TableCell>
                  {new Date(log.timestamp).toLocaleString()}
                </TableCell>
                <TableCell>{log.user?.username || 'System'}</TableCell>
                <TableCell>
                  <Chip
                    label={log.action}
                    color={actionColors[log.action] || 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>{log.model_name}</TableCell>
                <TableCell>{log.object_name || '-'}</TableCell>
                <TableCell>{log.ip_address || '-'}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </DashboardLayout>
  );
}
