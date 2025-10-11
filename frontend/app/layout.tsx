import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { ClerkProvider } from '@clerk/nextjs';
import UserSync from '../components/UserSync';
import '../styles/globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'CampusMind - AI Academic & Wellness Assistant',
  description:
    'AI-powered academic and wellness assistant for college students',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body className={inter.className}>
          <UserSync>{children}</UserSync>
        </body>
      </html>
    </ClerkProvider>
  );
}
