import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

export const AppLayout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="app-container">
      {/* Mobile Backdrop */}
      {sidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.6)',
            zIndex: 95,
          }}
        />
      )}

      <Sidebar isOpen={sidebarOpen} onCloseMobile={() => setSidebarOpen(false)} />

      <div className="main-content">
        <Header onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
        <main className="page-body">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
