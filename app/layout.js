import './globals.css';

export const metadata = {
  title: 'Resume Tool — AI-Powered Resume Cleanup',
  description: 'Paste your resume, get AI-powered suggestions and formatting',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen">{children}</body>
    </html>
  );
}
