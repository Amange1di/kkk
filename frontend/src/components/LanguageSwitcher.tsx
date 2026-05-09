'use client';

import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { FormControl, InputLabel, Select, MenuItem } from '@mui/material';

export default function LanguageSwitcher() {
  const { i18n, t } = useTranslation();
  const [currentLang, setCurrentLang] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const savedLang = localStorage.getItem('i18nextLng') || 'ru';
    setCurrentLang(savedLang);
    if (i18n.language !== savedLang) {
      i18n.changeLanguage(savedLang);
    }
  }, [i18n]);

  const handleChange = (event: any) => {
    const newLang = event.target.value;
    setCurrentLang(newLang);
    i18n.changeLanguage(newLang);
    localStorage.setItem('i18nextLng', newLang);
  };

  if (!mounted || currentLang === null) {
    return null;
  }

  return (
    <FormControl size="small" sx={{ minWidth: 100 }}>
      <InputLabel id="lang-select-label">{t('language')}</InputLabel>
      <Select
        labelId="lang-select-label"
        value={currentLang}
        label={t('language')}
        onChange={handleChange}
      >
        <MenuItem value="ru">Русский</MenuItem>
        <MenuItem value="ky">Кыргызча</MenuItem>
        <MenuItem value="en">English</MenuItem>
      </Select>
    </FormControl>
  );
}
