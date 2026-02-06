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
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem('darkMode') === 'true';
  });
  
  // Date filtering state
  const [dateFilter, setDateFilter] = useState({
    startDate: '',
    endDate: '',
  });
  
  // Add equipment modal state
  const [showAddModal, setShowAddModal] = useState(false);
  const [newEquipment, setNewEquipment] = useState({
    name: '',
    equipment_type: '',
    flowrate: 0,
    pressure: 0,
    temperature: 0,
  });

  // Apply dark mode class to body
  useEffect(() => {
    document.body.classList.toggle('dark-mode', darkMode);
    localStorage.setItem('darkMode', darkMode);
  }, [darkMode]);

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

  const refreshDataset = async () => {
    if (!selectedDataset) return;
    try {
      const response = await dataAPI.getDataset(selectedDataset);
      setCurrentData({
        summary: response.data.summary,
        equipment_list: response.data.equipment_list,
        dataset_id: selectedDataset,
        filename: response.data.filename,
      });
    } catch (error) {
      toast.error('Failed to refresh dataset');
    }
  };

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

  const handleDownloadCSV = async () => {
    if (!selectedDataset) {
      toast.error('Please select a dataset first');
      return;
    }

    try {
      const response = await dataAPI.downloadCSV(selectedDataset);
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `equipment_data_${selectedDataset}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.success('CSV downloaded successfully!');
    } catch (error) {
      toast.error('Failed to export CSV');
    }
  };

  // CRUD Operations
  const handleEditEquipment = async (equipmentId, updatedData) => {
    try {
      await dataAPI.updateEquipment(selectedDataset, equipmentId, updatedData);
      toast.success('Equipment updated successfully');
      await refreshDataset();
    } catch (error) {
      toast.error('Failed to update equipment');
    }
  };

  const handleDeleteEquipment = async (equipmentId) => {
    if (!window.confirm('Are you sure you want to delete this equipment?')) {
      return;
    }
    
    try {
      await dataAPI.deleteEquipment(selectedDataset, equipmentId);
      toast.success('Equipment deleted successfully');
      await refreshDataset();
    } catch (error) {
      toast.error('Failed to delete equipment');
    }
  };

  const handleAddEquipment = async () => {
    try {
      await dataAPI.addEquipment(selectedDataset, newEquipment);
      toast.success('Equipment added successfully');
      setShowAddModal(false);
      setNewEquipment({
        name: '',
        equipment_type: '',
        flowrate: 0,
        pressure: 0,
        temperature: 0,
      });
      await refreshDataset();
    } catch (error) {
      toast.error('Failed to add equipment');
    }
  };

  // Date filtering
  const handleApplyDateFilter = async () => {
    if (!selectedDataset) return;
    
    setLoading(true);
    try {
      const response = await dataAPI.getEquipmentList(selectedDataset, dateFilter);
      setCurrentData(prev => ({
        ...prev,
        equipment_list: response.data.equipment,
      }));
      toast.success(`Filtered: ${response.data.count} equipment found`);
    } catch (error) {
      toast.error('Failed to apply filter');
    } finally {
      setLoading(false);
    }
  };

  const handleClearDateFilter = async () => {
    setDateFilter({ startDate: '', endDate: '' });
    await refreshDataset();
  };

  const handleLogout = (e) => {
    e.preventDefault();
    e.stopPropagation();
    console.log('Logout button clicked - showing modal');
    setShowLogoutModal(true);
  };

  const confirmLogout = async () => {
    console.log('Confirm logout clicked');
    setShowLogoutModal(false);
    await logout();
    navigate('/login');
  };

  const cancelLogout = () => {
    console.log('Cancel logout clicked');
    setShowLogoutModal(false);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const toggleDarkMode = () => {
    setDarkMode(prev => !prev);
  };

  return (
    <div className={`dashboard ${darkMode ? 'dark-mode' : ''}`}>
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
            <li style={{ marginTop: '20px' }}>
              <button type="button" onClick={toggleDarkMode} className="theme-toggle">
                <span>{darkMode ? '☀️' : '🌙'}</span>
                <span>{darkMode ? 'Light Mode' : 'Dark Mode'}</span>
              </button>
            </li>
            <li style={{ marginTop: '10px' }}>
              <button type="button" onClick={handleLogout}>
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

                {/* Export & Filter Actions */}
                <div className="card" style={{ marginBottom: '25px' }}>
                  <div className="card-header">
                    <h3>Export Data</h3>
                  </div>
                  <div className="action-buttons">
                    <button className="btn btn-success btn-icon" onClick={handleDownloadPDF}>
                      📄 Download PDF Report
                    </button>
                    <button className="btn btn-primary btn-icon" onClick={handleDownloadCSV}>
                      📥 Export as CSV
                    </button>
                  </div>
                </div>

                {/* Date Filter */}
                <div className="card" style={{ marginBottom: '25px' }}>
                  <div className="card-header">
                    <h3>Filter by Date</h3>
                  </div>
                  <div className="date-filter">
                    <div className="filter-inputs">
                      <div className="filter-group">
                        <label>Start Date</label>
                        <input 
                          type="date" 
                          value={dateFilter.startDate}
                          onChange={(e) => setDateFilter(prev => ({ ...prev, startDate: e.target.value }))}
                        />
                      </div>
                      <div className="filter-group">
                        <label>End Date</label>
                        <input 
                          type="date" 
                          value={dateFilter.endDate}
                          onChange={(e) => setDateFilter(prev => ({ ...prev, endDate: e.target.value }))}
                        />
                      </div>
                    </div>
                    <div className="filter-actions">
                      <button className="btn btn-primary btn-sm" onClick={handleApplyDateFilter}>
                        Apply Filter
                      </button>
                      <button className="btn btn-secondary btn-sm" onClick={handleClearDateFilter}>
                        Clear Filter
                      </button>
                    </div>
                  </div>
                </div>

                {/* Data Table with CRUD */}
                <div className="card">
                  <div className="card-header">
                    <h3>Equipment List</h3>
                    <button 
                      className="btn btn-success btn-sm"
                      onClick={() => setShowAddModal(true)}
                    >
                      + Add Equipment
                    </button>
                  </div>
                  <DataTable 
                    data={currentData.equipment_list} 
                    editable={true}
                    onEdit={handleEditEquipment}
                    onDelete={handleDeleteEquipment}
                  />
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

      {/* Add Equipment Modal */}
      {showAddModal && (
        <div className="modal-overlay">
          <div className="modal-content modal-form">
            <div className="modal-icon">➕</div>
            <h3>Add New Equipment</h3>
            <div className="modal-form-fields">
              <div className="form-group">
                <label>Equipment Name</label>
                <input 
                  type="text" 
                  value={newEquipment.name}
                  onChange={(e) => setNewEquipment(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="e.g., Reactor-006"
                />
              </div>
              <div className="form-group">
                <label>Type</label>
                <input 
                  type="text" 
                  value={newEquipment.equipment_type}
                  onChange={(e) => setNewEquipment(prev => ({ ...prev, equipment_type: e.target.value }))}
                  placeholder="e.g., Reactor"
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Flowrate</label>
                  <input 
                    type="number" 
                    step="0.01"
                    value={newEquipment.flowrate}
                    onChange={(e) => setNewEquipment(prev => ({ ...prev, flowrate: parseFloat(e.target.value) || 0 }))}
                  />
                </div>
                <div className="form-group">
                  <label>Pressure</label>
                  <input 
                    type="number" 
                    step="0.01"
                    value={newEquipment.pressure}
                    onChange={(e) => setNewEquipment(prev => ({ ...prev, pressure: parseFloat(e.target.value) || 0 }))}
                  />
                </div>
                <div className="form-group">
                  <label>Temperature</label>
                  <input 
                    type="number" 
                    step="0.01"
                    value={newEquipment.temperature}
                    onChange={(e) => setNewEquipment(prev => ({ ...prev, temperature: parseFloat(e.target.value) || 0 }))}
                  />
                </div>
              </div>
            </div>
            <div className="modal-buttons">
              <button className="btn-cancel" onClick={() => setShowAddModal(false)}>
                Cancel
              </button>
              <button className="btn-confirm btn-add" onClick={handleAddEquipment}>
                Add Equipment
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
