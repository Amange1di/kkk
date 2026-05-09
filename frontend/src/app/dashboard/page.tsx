'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import {
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Inventory as AssetIcon,
  LocationOn as LocationIcon,
  SwapHoriz as TransferIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { reportsApi } from '@/services/api';
import { useTranslation } from 'react-i18next';

interface SummaryData {
  total: number;
  by_status: { status: string; count: number }[];
  by_type: { asset_type: string; count: number }[];
  recent_count: number;
}

export default function DashboardPage() {
  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { t } = useTranslation();

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await reportsApi.getSummary();
        setSummary(response.data);
      } catch {
        setError(t('error_loading_data'));
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, []);

  if (loading) {
    return (
      <DashboardLayout>
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout>
        <Alert severity="error">{error}</Alert>
      </DashboardLayout>
    );
  }

  const statusColors: Record<string, string> = {
    available: 'success',
    in_use: 'primary',
    in_repair: 'warning',
    retired: 'error',
    lost: 'error',
  };

  const statusLabels: Record<string, string> = {
    available: t('available'),
    in_use: t('in_use'),
    in_repair: t('in_repair'),
    retired: t('retired'),
    lost: t('lost'),
  };

  return (
    <DashboardLayout>
      <Typography variant="h4" gutterBottom>
        {t('dashboard')}
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
          <Box sx={{ flexGrow: 1, minWidth: '200px' }}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <AssetIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      {t('total_assets')}
                    </Typography>
                    <Typography variant="h4">
                      {summary?.total || 0}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>

          <Box sx={{ flexGrow: 1, minWidth: '200px' }}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <LocationIcon sx={{ fontSize: 40, color: 'success.main', mr: 2 }} />
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      {t('locations_label')}
                    </Typography>
                    <Typography variant="h4">--</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>

          <Box sx={{ flexGrow: 1, minWidth: '200px' }}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <TransferIcon sx={{ fontSize: 40, color: 'info.main', mr: 2 }} />
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      {t('recent_transfers')}
                    </Typography>
                    <Typography variant="h4">
                      {summary?.recent_count || 0}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>

          <Box sx={{ flexGrow: 1, minWidth: '200px' }}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <WarningIcon sx={{ fontSize: 40, color: 'warning.main', mr: 2 }} />
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      {t('in_repair')}
                    </Typography>
                    <Typography variant="h4">
                      {summary?.by_status?.find(s => s.status === 'in_repair')?.count || 0}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>
        </Box>

        <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
          <Box sx={{ flexGrow: 1, minWidth: '300px' }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {t('assets_by_status')}
                </Typography>
                <Box>
                  {summary?.by_status?.map((status) => (
                    <Box key={status.status} sx={{ mb: 1 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                          {statusLabels[status.status] || status.status.replace('_', ' ')}
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          {status.count}
                        </Typography>
                      </Box>
                      <Box
                        sx={{
                          width: '100%',
                          height: 8,
                          bgcolor: 'grey.200',
                          borderRadius: 1,
                          overflow: 'hidden',
                        }}
                      >
                        <Box
                          sx={{
                            width: `${(status.count / (summary?.total || 1)) * 100}%`,
                            height: '100%',
                            bgcolor: statusColors[status.status] || 'primary.main',
                          }}
                        />
                      </Box>
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Box>

          <Box sx={{ flexGrow: 1, minWidth: '300px' }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {t('assets_by_type')}
                </Typography>
                <Box>
                  {summary?.by_type?.map((type) => (
                    <Box key={type.asset_type} sx={{ mb: 1 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                          {type.asset_type.replace('_', ' ')}
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          {type.count}
                        </Typography>
                      </Box>
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Box>
        </Box>
      </Box>
    </DashboardLayout>
  );
}
