'use client';

import { useState, useRef } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import {
  Box,
  Button,
  TextField,
  Card,
  CardContent,
  Typography,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  CircularProgress,
  IconButton,
} from '@mui/material';
import {
  QrCodeScanner,
  Keyboard,
  Close,
  CheckCircle,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { assetsApi } from '@/services/api';
import { useTranslation } from 'react-i18next';

export default function ScanPage() {
  const { t } = useTranslation();
  const [scanMode, setScanMode] = useState<'manual' | 'camera'>('manual');
  const [assetTag, setAssetTag] = useState('');
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);

  const handleManualScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!assetTag.trim()) return;

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await assetsApi.scan(assetTag.trim());
      setResult(response.data);
      setShowDetails(true);
    } catch (err: any) {
      setError(err.response?.data?.message || t('asset_not_found'));
    } finally {
      setLoading(false);
    }
  };

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' },
      });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
      setScanMode('camera');
    } catch {
      setError(t('camera_access_denied'));
      setScanMode('manual');
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    setScanMode('manual');
  };

  return (
    <DashboardLayout>
      <Typography variant="h4" gutterBottom>
        {t('scan_qr')}
      </Typography>

      <Box sx={{ maxWidth: 600, mx: 'auto' }}>
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
              <Button
                variant={scanMode === 'manual' ? 'contained' : 'outlined'}
                onClick={() => setScanMode('manual')}
                startIcon={<Keyboard />}
              >
                {t('manual_entry')}
              </Button>
              <Button
                variant={scanMode === 'camera' ? 'contained' : 'outlined'}
                onClick={scanMode === 'camera' ? stopCamera : startCamera}
                startIcon={<QrCodeScanner />}
              >
                {scanMode === 'camera' ? t('stop_camera') : t('use_camera')}
              </Button>
            </Box>

            {scanMode === 'manual' ? (
              <Box component="form" onSubmit={handleManualScan}>
                <TextField
                  fullWidth
                  label={t('enter_asset_tag')}
                  value={assetTag}
                  onChange={(e) => setAssetTag(e.target.value)}
                  placeholder={t('example_asset_tag')}
                  variant="outlined"
                />
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  size="large"
                  sx={{ mt: 2 }}
                  disabled={loading || !assetTag.trim()}
                >
                  {loading ? <CircularProgress size={24} /> : t('search')}
                </Button>
              </Box>
            ) : (
              <Box sx={{ position: 'relative' }}>
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  style={{
                    width: '100%',
                    borderRadius: 8,
                    background: '#000',
                  }}
                />
                <Box
                  sx={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    width: 200,
                    height: 200,
                    border: '3px solid #1976d2',
                    borderRadius: 2,
                  }}
                />
              </Box>
            )}

            {error && (
              <Alert severity="error" sx={{ mt: 2 }} onClose={() => setError('')}>
                {error}
              </Alert>
            )}
          </CardContent>
        </Card>

        {result?.found && (
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <CheckCircle sx={{ color: 'success.main', mr: 1 }} />
                <Typography variant="h6">{t('asset_found')}</Typography>
              </Box>

              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                  {result.asset.asset_tag}
                </Typography>
                <Chip
                  label={t(result.asset.status_key) || result.asset.status_key}
                  color={
                    result.asset.status_key === 'available'
                      ? 'success'
                      : result.asset.status_key === 'in_use'
                      ? 'primary'
                      : 'warning'
                  }
                />
              </Box>

              <Typography variant="body1" gutterBottom>
                <strong>{t('name')}:</strong> {result.asset.name}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                <strong>{t('type')}:</strong> {result.asset.asset_type}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                <strong>{t('current_location')}:</strong> {result.asset.location || t('not_assigned')}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                <strong>{t('assigned_to')}:</strong> {result.asset.assigned_to || t('unassigned')}
              </Typography>

              <Box sx={{ mt: 2 }}>
                <Button
                  variant="outlined"
                  onClick={() => setShowDetails(true)}
                  fullWidth
                >
                  {t('view_full_details')}
                </Button>
              </Box>
            </CardContent>
          </Card>
        )}
      </Box>

      <Dialog open={showDetails} onClose={() => setShowDetails(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {t('asset_details')}
          <IconButton
            onClick={() => setShowDetails(false)}
            sx={{ position: 'absolute', right: 8, top: 8 }}
          >
            <Close />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          {result?.found && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {result.asset.asset_tag}
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body1"><strong>{t('name')}:</strong> {result.asset.name}</Typography>
                <Typography variant="body2" color="text.secondary"><strong>{t('type')}:</strong> {result.asset.asset_type}</Typography>
                <Typography variant="body2" color="text.secondary"><strong>{t('status')}:</strong> {t(result.asset.status) || result.asset.status}</Typography>
                <Typography variant="body2" color="text.secondary"><strong>{t('current_location')}:</strong> {result.asset.location || t('na')}</Typography>
                <Typography variant="body2" color="text.secondary"><strong>{t('assigned_to')}:</strong> {result.asset.assigned_to || t('na')}</Typography>
                <Typography variant="body2" color="text.secondary"><strong>{t('manufacturer')}:</strong> {result.asset.manufacturer || t('na')}</Typography>
                <Typography variant="body2" color="text.secondary"><strong>{t('model')}:</strong> {result.asset.model || t('na')}</Typography>
                <Typography variant="body2" color="text.secondary"><strong>{t('serial_number')}:</strong> {result.asset.serial_number || t('na')}</Typography>
                <Typography variant="body2" color="text.secondary"><strong>{t('purchase_date')}:</strong> {result.asset.purchase_date || t('na')}</Typography>
                <Typography variant="body2" color="text.secondary"><strong>{t('purchase_price')}:</strong> {result.asset.purchase_price || t('na')}</Typography>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowDetails(false)}>{t('close')}</Button>
        </DialogActions>
      </Dialog>
    </DashboardLayout>
  );
}
