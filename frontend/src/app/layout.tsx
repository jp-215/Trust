import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Trust — Fact Checker',
  description:
    'Aggregated news fact-checking: fact matrix, source-of-truth synthesis, and Gemini chat',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
