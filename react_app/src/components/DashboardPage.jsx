// src/components/DashboardPage.jsx
// NO CHANGES NEEDED compared to the previous version handling manufacturer RLS.
// The logic correctly adapts based on the 'mode' prop and URL parameters.

import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import './DashboardPage.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const SUPERSET_URL = import.meta.env.VITE_SUPERSET_URL;
const DASHBOARD_ID = import.meta.env.VITE_SUPERSET_DASHBOARD_ID;

const EMBED_DELAY_MS = 50;

function DashboardPage({ mode }) {
  // Get manufacturer from route parameters (only relevant for mode='rls')
  const { manufacturer } = useParams();
  const [guestToken, setGuestToken] = useState(null);
  const [error, setError] = useState(null);
  const [isLoadingToken, setIsLoadingToken] = useState(true);
  const [isEmbedding, setIsEmbedding] = useState(false);
  const dashboardContainerRef = useRef(null);
  const embedInstanceRef = useRef(null);
  const embedTimeoutRef = useRef(null);

  const fetchToken = useCallback(async () => {
    setIsLoadingToken(true);
    setError(null);
    setGuestToken(null);

    let tokenUrl = '';
    if (mode === 'rls') {
      if (!manufacturer) { // Check for manufacturer param for RLS mode
        setError('Manufacturer name is missing in URL for RLS dashboard.');
        setIsLoadingToken(false);
        return;
      }
      // Use 'manufacturer' query parameter for RLS token endpoint
      tokenUrl = `${API_BASE_URL}/get-guest-token-rls?manufacturer=${encodeURIComponent(manufacturer)}`;
    } else if (mode === 'full') {
      // Use identifier from local storage for the 'user_id' in full token endpoint
      // This will be 'admin' for the admin user, or manufacturer name if they access full view
      const userId = localStorage.getItem('userIdentifier') || 'react_full_user_fallback';
      tokenUrl = `${API_BASE_URL}/get-guest-token-full?user_id=${encodeURIComponent(userId)}`;
    } else {
      setError('Invalid dashboard mode specified.');
      setIsLoadingToken(false);
      return;
    }

    console.log(`[${mode}] Requesting token from: ${tokenUrl}`); // Log URL being called

    try {
      const response = await fetch(tokenUrl);
      if (!response.ok) {
        let errorDetail = `Failed to fetch guest token (${response.status})`;
        try { const errorData = await response.json(); errorDetail = errorData.detail || errorDetail; } catch (e) { /* Ignore */ }
        throw new Error(errorDetail);
      }
      const data = await response.json();
      if (!data.token) { throw new Error('Token not found in response from backend.'); }
      setGuestToken(data.token);
      console.log(`[${mode}] Guest Token fetched successfully.`);
    } catch (err) {
      console.error(`[${mode}] Error fetching guest token:`, err);
      setError(`Error fetching guest token: ${err.message}.`);
    } finally {
      setIsLoadingToken(false);
    }
  // Add manufacturer to dependency array for RLS mode, mode is always a dependency
  }, [mode, manufacturer]);

  // Effect to fetch token
  useEffect(() => {
    console.log(`[${mode}] Token fetching effect triggered.`);
    fetchToken();
  }, [fetchToken]); // fetchToken dependency includes mode and manufacturer

  // Effect to handle embedding AND cleanup
  useEffect(() => {
    console.log(`[${mode}] Embedding effect triggered. Token: ${guestToken ? 'Available' : 'Not Available'}, Container Ref: ${dashboardContainerRef.current ? 'Ready' : 'Not Ready'}`);
    const cleanupEmbedding = (reason = "unknown") => {
        console.log(`[${mode}] Running cleanup function. Reason: ${reason}.`);
      if (embedTimeoutRef.current) {
          clearTimeout(embedTimeoutRef.current);
          embedTimeoutRef.current = null;
      }
      if (embedInstanceRef.current && typeof embedInstanceRef.current.unmount === 'function') {
        try {
          console.log(`[${mode}] Attempting to unmount previous dashboard instance via SDK...`);
          embedInstanceRef.current.unmount();
        } catch (unmountError) {
          console.error(`[${mode}] Error during SDK unmount call:`, unmountError);
        }
        embedInstanceRef.current = null;
      }
      setIsEmbedding(false); // Ensure state is reset
    };

    if (guestToken && dashboardContainerRef.current) {
      console.log(`[${mode}] Conditions met for embedding. Proceeding with delay.`);
      embedTimeoutRef.current = setTimeout(async () => {
          console.log(`[${mode}] Delay finished. Starting embed process.`);
          embedTimeoutRef.current = null;
          if (typeof window.supersetEmbeddedSdk === 'undefined' || typeof window.supersetEmbeddedSdk.embedDashboard !== 'function') {
            console.error('CRITICAL: Superset Embedded SDK or embedDashboard function not found.');
            setError('Error: Superset Embedded SDK not loaded correctly.');
            setIsEmbedding(false);
            return;
          }

          const embedConfig = {
            id: DASHBOARD_ID,
            supersetDomain: SUPERSET_URL,
            mountPoint: dashboardContainerRef.current,
            fetchGuestToken: () => Promise.resolve(guestToken), // Use the fetched token
            dashboardUiConfig: { hideTitle: true },
          };
          console.log(`[${mode}] Embedding with config:`, JSON.stringify({ ...embedConfig, mountPoint: 'HTMLElement', fetchGuestToken: 'Function' }));

          setIsEmbedding(true);
          setError(null); // Clear previous errors before trying to embed

          try {
            if (dashboardContainerRef.current) {
                // Ensure container is empty before embedding
                dashboardContainerRef.current.innerHTML = '';
                console.log(`[${mode}] Cleared container just before embedding.`);
            }
            embedInstanceRef.current = await window.supersetEmbeddedSdk.embedDashboard(embedConfig);
            console.log(`[${mode}] embedDashboard promise resolved. Instance:`, embedInstanceRef.current);
            setIsEmbedding(false); // Embedding initiated successfully
          } catch (embeddingError) {
            console.error(`[${mode}] CRITICAL ERROR during supersetEmbeddedSdk.embedDashboard call:`, embeddingError);
            setError(`Failed to embed dashboard: ${embeddingError.message || embeddingError}`);
            setIsEmbedding(false);
          }
      }, EMBED_DELAY_MS);
      console.log(`[${mode}] Scheduled embedding with timeout ID: ${embedTimeoutRef.current}`);
    } else {
        console.log(`[${mode}] Conditions not met for embedding. Token: ${!!guestToken}, Container: ${!!dashboardContainerRef.current}. Running cleanup.`);
        // Run cleanup if conditions aren't met (e.g., token fetch failed)
        cleanupEmbedding("conditions_not_met");
    }

    // Return the Cleanup Function
    return () => cleanupEmbedding("effect_rerun_or_unmount");

  // Add manufacturer to dependency array as it influences the token fetch for RLS
  }, [guestToken, mode, manufacturer]);

  // Determine the title based on mode and potentially the manufacturer param
  const pageTitle = mode === 'rls'
    ? `Dashboard View: Filtered for ${manufacturer || 'Unknown Manufacturer'}`
    : 'Dashboard View: Full Access';

  return (
    <div className="dashboard-page-container">
      <h2>{pageTitle}</h2>

      {isLoadingToken && <div className="loading">Loading Access Token...</div>}
      {error && <div className="error-message dashboard-error">{error}</div>}

      <div ref={dashboardContainerRef} id="dashboard-container" className="dashboard-embed-container">
        {/* Show embedding message only when actively trying */}
        {!isLoadingToken && !error && isEmbedding && <div className="loading">Embedding Dashboard...</div>}
        {/* Show message if token failed or isn't available and not currently trying to embed */}
        {!isLoadingToken && !error && !guestToken && !isEmbedding && <div>Token not available or embedding failed. Please check console for errors.</div>}
        {/* SDK places iframe here */}
      </div>
    </div>
  );
}

export default DashboardPage;