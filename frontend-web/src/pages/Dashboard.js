import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { dataAPI } from '../services/api';
import { toast } from 'react-toastify';
import FileUpload from '../components/FileUpload/FileUpload';
import DataTable from '../components/DataTable/DataTable';
import {
  TypeDistributionChart,
  ParameterComparisonChart,
  TypeCountChart,
} from '../components/Charts/Charts';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
  const [activeTab, setActiveTab] = useState('upload');
  const [currentData, setCurrentData] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [showLogoutModal, setShowLogoutModal] = useState(false);

  const fetchHistory = useCallback(async () => {
    try {
      const response = await dataAPI.getHistory();
      setHistory(response.data.datasets || []);
    } catch (error) {
      console.error('Error fetching history:', error);
    }
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const handleUploadSuccess = (data) => {
    setCurrentData({
      summary: data.summary,
      equipment_list: data.equipment_list,
      dataset_id: data.dataset_id,
    });
    setSelectedDataset(data.dataset_id);
    setActiveTab('data');
    fetchHistory();
  };

  const handleSelectDataset = async (dataset) => {
    setLoading(true);
    setSelectedDataset(dataset.id);
    
    try {
      const response = await dataAPI.getDataset(dataset.id);
      setCurrentData({
        summary: response.data.summary,
        equipment_list: response.data.equipment_list,
        dataset_id: dataset.id,
        filename: response.data.filename,
      });
      setActiveTab('data');
    } catch (error) {
      toast.error('Failed to load dataset');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDataset = async (datasetId, e) => {
    e.stopPropagation();
    
    if (!window.confirm('Are you sure you want to delete this dataset?')) {
      return;
    }

    try {
      await dataAPI.deleteDataset(datasetId);
      toast.success('Dataset deleted successfully');
      
      if (selectedDataset === datasetId) {
        setCurrentData(null);
        setSelectedDataset(null);
      }
      
      fetchHistory();
    } catch (error) {
      toast.error('Failed to delete dataset');
    }
  };

  const handleDownloadPDF = async () => {
    if (!selectedDataset) {
      toast.error('Please select a dataset first');
      return;
    }

    try {
      const response = await dataAPI.downloadPDF(selectedDataset);
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `equipment_report_${selectedDataset}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.success('PDF downloaded successfully!');
    } catch (error) {
      toast.error('Failed to generate PDF');
    }
  };

  const handleLogout = () => {
    setShowLogoutModal(true);
  };

  const confirmLogout = async () => {
    await logout();
    navigate('/login');
  };

  const cancelLogout = () => {
    setShowLogoutModal(false);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="dashboard">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span style={{ fontSize: '24px' }}>🔬</span>
          <h1>Chemical Viz</h1>
        </div>
        
        <nav>
          <ul className="sidebar-nav">
            <li>
              <a 
                href="#upload" 
                className={activeTab === 'upload' ? 'active' : ''}
                onClick={(e) => { e.preventDefault(); setActiveTab('upload'); }}
              >
                <span>📤</span>
                <span>Upload CSV</span>
              </a>
            </li>
            <li>
              <a 
                href="#data" 
                className={activeTab === 'data' ? 'active' : ''}
                onClick={(e) => { e.preventDefault(); setActiveTab('data'); }}
              >
                <span>📊</span>
                <span>View Data</span>
              </a>
            </li>
            <li>
              <a 
                href="#charts" 
                className={activeTab === 'charts' ? 'active' : ''}
                onClick={(e) => { e.preventDefault(); setActiveTab('charts'); }}
              >
                <span>📈</span>
                <span>Charts</span>
              </a>
            </li>
            <li>
              <a 
                href="#history" 
                className={activeTab === 'history' ? 'active' : ''}
                onClick={(e) => { e.preventDefault(); setActiveTab('history'); }}
              >
                <span>📋</span>
                <span>History</span>
              </a>
            </li>
            <li style={{ marginTop: '30px' }}>
              <button onClick={handleLogout}>
                <span>🚪</span>
                <span>Logout</span>
              </button>
            </li>
          </ul>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {/* Header */}
        <header className="header">
          <h2>
            {activeTab === 'upload' && 'Upload Equipment Data'}
            {activeTab === 'data' && 'Equipment Data'}
            {activeTab === 'charts' && 'Data Visualization'}
            {activeTab === 'history' && 'Upload History'}
          </h2>
          
          <div className="user-info">
            <div className="user-avatar">
              {user?.username?.charAt(0).toUpperCase()}
            </div>
            <span>{user?.username}</span>
          </div>
        </header>

        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <div className="card">
            <div className="card-header">
              <h3>Upload CSV File</h3>
            </div>
            <FileUpload onUploadSuccess={handleUploadSuccess} />
          </div>
        )}

        {/* Data Tab */}
        {activeTab === 'data' && (
          <>
            {currentData ? (
              <>
                {/* Stats */}
                <div className="stats-grid">
                  <div className="stat-card highlight">
                    <h4>Total Equipment</h4>
                    <div className="value">{currentData.summary.total_equipment}</div>
                  </div>
                  <div className="stat-card">
                    <h4>Avg Flowrate</h4>
                    <div className="value">{currentData.summary.avg_flowrate.toFixed(2)}</div>
                  </div>
                  <div className="stat-card">
                    <h4>Avg Pressure</h4>
                    <div className="value">{currentData.summary.avg_pressure.toFixed(2)}</div>
                  </div>
                  <div className="stat-card">
                    <h4>Avg Temperature</h4>
                    <div className="value">{currentData.summary.avg_temperature.toFixed(2)}</div>
                  </div>
                </div>

                {/* Actions */}
                <div className="card" style={{ marginBottom: '25px' }}>
                  <div className="action-buttons">
                    <button className="btn btn-success btn-icon" onClick={handleDownloadPDF}>
                      📄 Download PDF Report
                    </button>
                  </div>
                </div>

                {/* Data Table */}
                <div className="card">
                  <div className="card-header">
                    <h3>Equipment List</h3>
                  </div>
                  <DataTable data={currentData.equipment_list} />
                </div>
              </>
            ) : (
              <div className="card">
                <div className="empty-state">
                  <h3>No data loaded</h3>
                  <p>Upload a CSV file or select from history to view data</p>
                </div>
              </div>
            )}
          </>
        )}

        {/* Charts Tab */}
        {activeTab === 'charts' && (
          <>
            {currentData ? (
              <div className="charts-grid">
                <div className="chart-container">
                  <h3>Equipment Type Distribution</h3>
                  <TypeDistributionChart data={currentData.summary.type_distribution} />
                </div>
                <div className="chart-container">
                  <h3>Equipment Count by Type</h3>
                  <TypeCountChart data={currentData.summary.type_distribution} />
                </div>
                <div className="chart-container" style={{ gridColumn: '1 / -1' }}>
                  <h3>Average Parameters by Equipment Type</h3>
                  <ParameterComparisonChart data={currentData.equipment_list} />
                </div>
              </div>
            ) : (
              <div className="card">
                <div className="empty-state">
                  <h3>No data loaded</h3>
                  <p>Upload a CSV file or select from history to view charts</p>
                </div>
              </div>
            )}
          </>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div className="card">
            <div className="card-header">
              <h3>Recent Uploads (Last 5)</h3>
            </div>
            
            {loading ? (
              <div className="loading-spinner">
                <div className="spinner"></div>
              </div>
            ) : history.length > 0 ? (
              <ul className="history-list">
                {history.map((dataset) => (
                  <li 
                    key={dataset.id} 
                    className={`history-item ${selectedDataset === dataset.id ? 'active' : ''}`}
                    onClick={() => handleSelectDataset(dataset)}
                  >
                    <div className="history-info">
                      <h4>{dataset.filename}</h4>
                      <span className="history-date">{formatDate(dataset.uploaded_at)}</span>
                    </div>
                    <div className="history-stats">
                      <div>{dataset.total_equipment} equipment</div>
                      <button 
                        className="btn btn-danger btn-sm"
                        style={{ marginTop: '8px', padding: '4px 12px' }}
                        onClick={(e) => handleDeleteDataset(dataset.id, e)}
                      >
                        Delete
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="empty-state">
                <h3>No upload history</h3>
                <p>Upload your first CSV file to get started</p>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Logout Confirmation Modal */}
      {showLogoutModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-icon">🚪</div>
            <h3>Confirm Logout</h3>
            <p>Are you sure you want to logout?</p>
            <div className="modal-buttons">
              <button className="btn-cancel" onClick={cancelLogout}>
                Cancel
              </button>
              <button className="btn-confirm" onClick={confirmLogout}>
                Yes, Logout
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
