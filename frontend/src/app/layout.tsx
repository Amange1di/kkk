import { CssBaseline, ThemeProvider } from '@mui/material';
import { AuthProvider } from '@/context/AuthContext';
import theme from '@/theme/theme';
import I18nInitializer from '@/components/I18nInitializer';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <I18nInitializer />
          <AuthProvider>{children}</AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}