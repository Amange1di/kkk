"use client";

import { useState, useEffect } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import {
  Box,
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
  IconButton,
  Tooltip,
  Alert,
  Pagination,
  Typography,
} from "@mui/material";
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  QrCode as QrIcon,
  CheckCircle as CheckInIcon,
  FileDownload as DownloadIcon,
  Search as SearchIcon,
  Close as CloseIcon,
} from "@mui/icons-material";
import { assetsApi, reportsApi } from "@/services/api";
import type { Asset, Location } from "@/services/api";
import { useTranslation } from "react-i18next";
import Autocomplete from "@mui/material/Autocomplete";
import axios from "axios";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "https://kkk-fwjw.onrender.com/api";

const STATUS_COLORS: Record<string, string> = {
  available: "success",
  in_use: "primary",
  in_repair: "warning",
  retired: "error",
  lost: "error",
};

const ASSET_TYPES = ["hardware", "software", "furniture", "vehicle", "other"];

export default function AssetsPage() {
  const { t } = useTranslation();
  const [assets, setAssets] = useState<Asset[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [openDialog, setOpenDialog] = useState(false);
  const [editingAsset, setEditingAsset] = useState<Asset | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [page, setPage] = useState(1);
  const rowsPerPage = 10;
  const [qrCodeDialog, setQrCodeDialog] = useState(false);
  const [qrCodeData, setQrCodeData] = useState<string>("");
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);

  const [formData, setFormData] = useState<Partial<Asset>>({
    asset_tag: "",
    name: "",
    asset_type: "hardware",
    status: "available",
    manufacturer: "",
    model: "",
    serial_number: "",
    purchase_price: "",
    auditor: "",
    auditor_user_id: undefined,
  });

  const fetchQrCode = async (assetId: number) => {
    try {
      const response = await assetsApi.getQrCode(assetId);
      setQrCodeData(response.data.qr_code);
      setSelectedAsset(response.data);
      setQrCodeDialog(true);
    } catch (error) {
      setError(t("failed_to_generate_qr"));
    }
  };

  const handleQrCodeClose = () => {
    setQrCodeDialog(false);
    setQrCodeData("");
    setSelectedAsset(null);
  };

  useEffect(() => {
    fetchAssets();
    fetchLocations();
    fetchUsers();
  }, []);

  const fetchAssets = async () => {
    try {
      const response = await assetsApi.getAll({ search: searchTerm });
      setAssets(response.data.results || response.data);
    } catch {
      setError(t("error_loading_data"));
    } finally {
      setLoading(false);
    }
  };

  const fetchLocations = async () => {
    try {
      const response = await axios.get(`${API_URL}/locations/`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      setLocations(response.data.results || response.data);
    } catch {}
  };

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API_URL}/accounts/users/`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      setUsers(response.data.results || response.data);
    } catch {}
  };

  const handleOpenDialog = (asset?: Asset) => {
    if (asset) {
      setEditingAsset(asset);
      setFormData(asset);
    } else {
      setEditingAsset(null);
      setFormData({
        asset_tag: "",
        name: "",
        asset_type: "hardware",
        status: "available",
        manufacturer: "",
        model: "",
        serial_number: "",
        purchase_price: "",
        auditor: "",
        auditor_user_id: undefined,
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingAsset(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingAsset) {
        await assetsApi.update(editingAsset.id, formData);
      } else {
        await assetsApi.create(formData);
      }
      handleCloseDialog();
      fetchAssets();
    } catch {
      setError(t("error_loading_data"));
    }
  };

  const handleDelete = async (id: number) => {
    if (confirm(t("confirm_delete"))) {
      try {
        await assetsApi.delete(id);
        fetchAssets();
      } catch {
        setError(t("error_loading_data"));
      }
    }
  };

  const handleExport = async (format: "csv" | "excel" | "pdf") => {
    try {
      const response = await reportsApi.exportAssets(format);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `assets.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch {
      setError(t("error_loading_data"));
    }
  };

  const filteredAssets = assets.filter(
    (asset) =>
      asset.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      asset.asset_tag.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  const paginatedAssets = filteredAssets.slice(
    (page - 1) * rowsPerPage,
    page * rowsPerPage,
  );

  return (
    <DashboardLayout>
      <Box sx={{ mb: 3 }}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 2,
          }}
        >
          <Typography variant="h4">{t("assets")}</Typography>
          <Box sx={{ display: "flex", gap: 1 }}>
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={() => handleExport("csv")}
            >
              {t("csv")}
            </Button>
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={() => handleExport("excel")}
            >
              {t("excel")}
            </Button>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleOpenDialog()}
            >
              {t("add_asset")}
            </Button>
          </Box>
        </Box>

        <Box sx={{ display: "flex", gap: 2, mb: 2 }}>
          <TextField
            placeholder={t("search_assets")}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            slotProps={{
              input: {
                startAdornment: (
                  <SearchIcon sx={{ mr: 1, color: "text.secondary" }} />
                ),
              },
            }}
            sx={{ flexGrow: 1 }}
            size="small"
          />
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError("")}>
            {error}
          </Alert>
        )}

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>{t("asset_tag")}</TableCell>
                <TableCell>{t("name")}</TableCell>
                <TableCell>{t("type")}</TableCell>
                <TableCell>{t("status")}</TableCell>
                <TableCell>{t("current_location")}</TableCell>
                <TableCell>{t("auditor")}</TableCell>
                <TableCell>{t("responsible_user")}</TableCell>
                <TableCell>{t("assigned_to")}</TableCell>
                <TableCell>{t("actions")}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedAssets.map((asset) => (
                <TableRow key={asset.id}>
                  <TableCell>{asset.asset_tag}</TableCell>
                  <TableCell>{asset.name}</TableCell>
                  <TableCell>{asset.asset_type}</TableCell>
                  <TableCell>
                    <Chip
                      label={t(asset.status) || asset.status.replace("_", " ")}
                      color={STATUS_COLORS[asset.status] as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{asset.current_location?.name || "-"}</TableCell>
                  <TableCell>{asset.auditor || "-"}</TableCell>
                  <TableCell>{asset.auditor_user?.username || "-"}</TableCell>
                  <TableCell>
                    {asset.assigned_to?.username || t("not_assigned")}
                  </TableCell>
                  <TableCell>
                    <Tooltip title={t("asset_found")}>
                      <IconButton
                        size="small"
                        color="primary"
                        onClick={() => fetchQrCode(asset.id)}
                      >
                        <QrIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title={t("edit")}>
                      <IconButton
                        size="small"
                        onClick={() => handleOpenDialog(asset)}
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title={t("delete")}>
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDelete(asset.id)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
              {paginatedAssets.length === 0 && (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    {t("no_assets_found")}
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>

        <Box sx={{ mt: 2, display: "flex", justifyContent: "center" }}>
          <Pagination
            count={Math.ceil(filteredAssets.length / rowsPerPage)}
            page={page}
            onChange={(e, value) => setPage(value)}
            color="primary"
          />
        </Box>
      </Box>

      <Dialog
        open={openDialog}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editingAsset ? t("edit_asset") : t("add_asset")}
        </DialogTitle>
        <form onSubmit={handleSubmit}>
          <DialogContent>
            <Box
              sx={{
                display: "grid",
                gridTemplateColumns: "repeat(2, 1fr)",
                gap: 2,
              }}
            >
              <TextField
                fullWidth
                label={t("asset_tag")}
                value={formData.asset_tag}
                onChange={(e) =>
                  setFormData({ ...formData, asset_tag: e.target.value })
                }
                required
              />
              <TextField
                fullWidth
                label={t("name")}
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                required
              />
              <FormControl fullWidth required>
                <InputLabel>{t("type")}</InputLabel>
                <Select
                  value={formData.asset_type}
                  label={t("type")}
                  onChange={(e) =>
                    setFormData({ ...formData, asset_type: e.target.value })
                  }
                >
                  <MenuItem value="hardware">{t("hardware")}</MenuItem>
                  <MenuItem value="software">{t("software")}</MenuItem>
                  <MenuItem value="furniture">{t("furniture")}</MenuItem>
                  <MenuItem value="vehicle">{t("vehicle")}</MenuItem>
                  <MenuItem value="other">{t("other")}</MenuItem>
                </Select>
              </FormControl>
              <FormControl fullWidth required>
                <InputLabel>{t("status")}</InputLabel>
                <Select
                  value={formData.status}
                  label={t("status")}
                  onChange={(e) =>
                    setFormData({ ...formData, status: e.target.value })
                  }
                >
                  <MenuItem value="available">{t("available")}</MenuItem>
                  <MenuItem value="in_use">{t("in_use")}</MenuItem>
                  <MenuItem value="in_repair">{t("in_repair")}</MenuItem>
                  <MenuItem value="retired">{t("retired")}</MenuItem>
                  <MenuItem value="lost">{t("lost")}</MenuItem>
                </Select>
              </FormControl>
              <TextField
                fullWidth
                label={t("manufacturer")}
                value={formData.manufacturer}
                onChange={(e) =>
                  setFormData({ ...formData, manufacturer: e.target.value })
                }
              />
              <TextField
                fullWidth
                label={t("model")}
                value={formData.model}
                onChange={(e) =>
                  setFormData({ ...formData, model: e.target.value })
                }
              />
              <TextField
                fullWidth
                label={t("serial_number")}
                value={formData.serial_number}
                onChange={(e) =>
                  setFormData({ ...formData, serial_number: e.target.value })
                }
              />
              <TextField
                fullWidth
                label={t("purchase_price")}
                type="number"
                value={formData.purchase_price}
                onChange={(e) =>
                  setFormData({ ...formData, purchase_price: e.target.value })
                }
              />
              <Autocomplete
                fullWidth
                options={locations}
                getOptionLabel={(option) => option.name || ""}
                value={
                  locations.find((l) => l.name === formData.auditor) || null
                }
                onChange={(e, value) =>
                  setFormData({ ...formData, auditor: value?.name || "" })
                }
                renderInput={(params) => (
                  <TextField {...params} label={t("auditorium_room")} />
                )}
              />
              <Autocomplete
                fullWidth
                options={users}
                getOptionLabel={(option) => option.username || ""}
                value={
                  users.find((u) => u.id === formData.auditor_user_id) || null
                }
                onChange={(e, value) =>
                  setFormData({
                    ...formData,
                    auditor_user_id: value?.id || undefined,
                  })
                }
                renderInput={(params) => (
                  <TextField {...params} label={t("responsible_user")} />
                )}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>{t("cancel")}</Button>
            <Button type="submit" variant="contained">
              {editingAsset ? t("save") : t("save")}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      <Dialog open={qrCodeDialog} onClose={handleQrCodeClose} maxWidth="xs">
        <DialogTitle>
          QR Code - {selectedAsset?.asset_tag}
          <IconButton
            onClick={handleQrCodeClose}
            sx={{ position: "absolute", right: 8, top: 8 }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              py: 4,
            }}
          >
            {qrCodeData && (
              <Box
                component="img"
                src={qrCodeData}
                alt={t("qr_code")}
                sx={{ maxWidth: "100%", height: "auto" }}
              />
            )}
            <Typography variant="h6" sx={{ mt: 3 }}>
              {selectedAsset?.name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {selectedAsset?.asset_tag}
            </Typography>
            <Button
              variant="contained"
              startIcon={<DownloadIcon />}
              onClick={() => {
                if (!qrCodeData) return;
                const link = document.createElement("a");
                link.href = qrCodeData;
                link.download = `qr_${selectedAsset?.asset_tag || "asset"}.png`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
              }}
              sx={{ mt: 3 }}
            >
              {t("download_qr")}
            </Button>
          </Box>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
}
