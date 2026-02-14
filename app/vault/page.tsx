"use client";

import { useState, useEffect } from "react";
import { SpecterNav } from "@/components/landing/specter-nav";
import { VaultHeader } from "@/components/vault/vault-header";
import { VaultFilters } from "@/components/vault/vault-filters";
import { IncidentGrid } from "@/components/vault/incident-grid";

export default function VaultPage() {
  const [activeFilter, setActiveFilter] = useState("all");
  const [incidents, setIncidents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch incidents from backend
  useEffect(() => {
    const fetchIncidents = async () => {
      try {
        setIsLoading(true);
        const response = await fetch("http://localhost:8000/api/incidents?limit=100");
        
        if (!response.ok) {
          throw new Error(`Failed to fetch incidents: ${response.status}`);
        }
        
        const data = await response.json();
        setIncidents(data.incidents || []);
        setError(null);
      } catch (err: any) {
        console.error("Error fetching incidents:", err);
        setError(err.message || "Failed to load incidents");
      } finally {
        setIsLoading(false);
      }
    };

    fetchIncidents();
    
    // Connect to WebSocket for real-time updates
    const ws = new WebSocket("ws://localhost:8000/ws");
    
    ws.onopen = () => {
      console.log("Vault: Connected to backend for real-time updates");
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        // Refresh incidents when test completes or new diagnostic available
        if (data.type === "test_complete" || data.type === "diagnostic_update") {
          fetchIncidents();
        }
      } catch (error) {
        console.error("Vault WebSocket error:", error);
      }
    };
    
    ws.onerror = (error) => {
      console.error("Vault WebSocket connection error:", error);
    };
    
    ws.onclose = () => {
      console.log("Vault WebSocket disconnected");
    };
    
    // Poll for updates every 30 seconds as backup
    const interval = setInterval(fetchIncidents, 30000);
    
    return () => {
      clearInterval(interval);
      ws.close();
    };
  }, []);

  return (
    <main className="relative min-h-screen bg-[#050505] text-white overflow-hidden selection:bg-emerald-500/30">
      {/* Grain overlay */}
      <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden opacity-[0.03]">
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] brightness-100 contrast-150"></div>
      </div>

      {/* Scanline effect */}
      <div className="fixed inset-0 pointer-events-none z-50 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.1)_50%)] bg-[length:100%_4px] opacity-20"></div>

      {/* Background grid */}
      <div className="fixed inset-0 z-0 opacity-10 pointer-events-none">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:40px_40px]"></div>
      </div>

      {/* Page Content */}
      <div className="relative z-10 flex flex-col min-h-screen">
        <SpecterNav />

        <div className="flex-1 px-8 py-12 max-w-7xl mx-auto w-full mb-20 mt-28">
          <VaultHeader totalIncidents={incidents.length} />
          <VaultFilters
            activeFilter={activeFilter}
            onFilterChange={setActiveFilter}
          />
          
          {isLoading && incidents.length === 0 ? (
            <div className="text-center py-20">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-emerald-500 border-t-transparent"></div>
              <p className="mt-4 text-zinc-400">Loading incidents...</p>
            </div>
          ) : error && incidents.length === 0 ? (
            <div className="text-center py-20">
              <p className="text-red-400 mb-2">⚠️ {error}</p>
              <p className="text-zinc-500 text-sm">Make sure the backend is running on port 8000</p>
            </div>
          ) : null}
          
          <IncidentGrid 
            activeFilter={activeFilter} 
            incidents={incidents}
            isLoading={isLoading}
          />
        </div>
      </div>
    </main>
  );
}
