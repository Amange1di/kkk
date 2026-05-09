'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  CircularProgress,
} from '@mui/material';
import {
  FileDownload,
  Assignment,
  Timeline,
} from '@mui/icons-material';
import { reportsApi } from '@/services/api';
import { useTranslation } from 'react-i18next';

export default function ReportsPage() {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [auditLogs, setAuditLogs] = useState<any[]>([]);

  useEffect(() => {
    fetchAuditLogs();
  }, []);

  const fetchAuditLogs = async () => {
    try {
      const response = await reportsApi.getAuditLogs({ ordering: '-timestamp' });
      setAuditLogs(response.data.results || response.data);
    } catch {
      setError(t('error_loading_data'));
    }
  };

  const handleExport = async (format: 'csv' | 'excel' | 'pdf') => {
    setLoading(true);
    setError('');
    try {
      const response = await reportsApi.exportAssets(format);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `assets_report_${Date.now()}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch {
      setError(t('error_loading_data'));
    } finally {
      setLoading(false);
    }
  };

  const actionColors: Record<string, string> = {
    create: 'success',
    update: 'info',
    delete: 'error',
    transfer: 'warning',
    scan: 'primary',
    checkout: 'info',
    checkin: 'success',
    report_damage: 'error',
    export: 'info',
  };

  const actionLabels: Record<string, string> = {
    create: t('create'),
    update: t('update'),
    delete: t('delete'),
    transfer: t('transfer'),
    scan: t('scan'),
    checkout: t('checkout'),
    checkin: t('checkin'),
    report_damage: t('report_damage'),
    export: t('export'),
  };

  return (
    <DashboardLayout>
      <Typography variant="h4" gutterBottom>
        {t('reports')}
      </Typography>

      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Button
          variant="outlined"
          startIcon={<FileDownload />}
          onClick={() => handleExport('csv')}
          disabled={loading}
        >
          {t('csv')}
        </Button>
        <Button
          variant="outlined"
          startIcon={<FileDownload />}
          onClick={() => handleExport('excel')}
          disabled={loading}
        >
          {t('excel')}
        </Button>
        <Button
          variant="outlined"
          startIcon={<FileDownload />}
          onClick={() => handleExport('pdf')}
          disabled={loading}
        >
          {t('pdf')}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Timeline sx={{ mr: 1 }} />
            <Typography variant="h6">{t('audit_logs')}</Typography>
          </Box>

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
                {auditLogs.slice(0, 10).map((log) => (
                  <TableRow key={log.id}>
                    <TableCell>
                      {new Date(log.timestamp).toLocaleString()}
                    </TableCell>
                    <TableCell>{log.user?.username || 'System'}</TableCell>
                    <TableCell>
                      <Chip
                        label={actionLabels[log.action] || log.action}
                        color={actionColors[log.action] as any}
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
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Assignment sx={{ mr: 1 }} />
            <Typography variant="h6">{t('quick_actions')}</Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Button variant="contained" href="/assets">
              {t('manage_assets')}
            </Button>
            <Button variant="contained" href="/locations">
              {t('manage_locations')}
            </Button>
            <Button variant="contained" href="/scan">
              {t('scan_qr_code')}
            </Button>
          </Box>
        </CardContent>
      </Card>
    </DashboardLayout>
  );
}
