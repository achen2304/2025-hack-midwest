'use client';

import { useAuth } from '@clerk/nextjs';
import { useEffect, useState, useRef } from 'react';

interface UserSyncProps {
  children: React.ReactNode;
}

export default function UserSync({ children }: UserSyncProps) {
  const { getToken, isSignedIn, isLoaded } = useAuth();
  const [isSynced, setIsSynced] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const hasAttemptedSync = useRef(false);

  useEffect(() => {
    const syncUser = async () => {
      // Prevent multiple attempts
      if (
        !isLoaded ||
        !isSignedIn ||
        isSynced ||
        isLoading ||
        hasAttemptedSync.current
      ) {
        return;
      }

      hasAttemptedSync.current = true;
      setIsLoading(true);

      try {
        const token = await getToken();

        if (!token) {
          console.warn('No token available for user sync');
          return;
        }

        // Use the correct backend URL (port 8000)
        const apiUrl =
          process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

        const response = await fetch(`${apiUrl}/auth/sync-user`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const data = await response.json();
          console.log('User synced successfully:', data);
          setIsSynced(true);
        } else {
          console.error('Failed to sync user:', await response.text());
        }
      } catch (error) {
        console.error('Error syncing user:', error);
      } finally {
        setIsLoading(false);
      }
    };

    syncUser();
  }, [isLoaded, isSignedIn, getToken]); // Removed isSynced and isLoading from dependencies

  return <>{children}</>;
}
