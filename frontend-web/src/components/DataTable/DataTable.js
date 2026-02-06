import React, { useState } from 'react';

const DataTable = ({ data, onEdit, onDelete, editable = false }) => {
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});

  if (!data || data.length === 0) {
    return (
      <div className="empty-state">
        <h3>No data available</h3>
        <p>Upload a CSV file to see the equipment data here</p>
      </div>
    );
  }

  const handleEditClick = (item) => {
    setEditingId(item.id);
    setEditForm({
      name: item.name,
      equipment_type: item.type || item.equipment_type,
      flowrate: item.flowrate,
      pressure: item.pressure,
      temperature: item.temperature,
    });
  };

  const handleSaveClick = async (item) => {
    if (onEdit) {
      await onEdit(item.id, editForm);
    }
    setEditingId(null);
    setEditForm({});
  };

  const handleCancelClick = () => {
    setEditingId(null);
    setEditForm({});
  };

  const handleInputChange = (field, value) => {
    setEditForm(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="data-table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th>Equipment Name</th>
            <th>Type</th>
            <th>Flowrate</th>
            <th>Pressure</th>
            <th>Temperature</th>
            {editable && <th>Actions</th>}
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr key={item.id || index}>
              {editingId === item.id ? (
                <>
                  <td>
                    <input
                      type="text"
                      value={editForm.name}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                      className="edit-input"
                    />
                  </td>
                  <td>
                    <input
                      type="text"
                      value={editForm.equipment_type}
                      onChange={(e) => handleInputChange('equipment_type', e.target.value)}
                      className="edit-input"
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      step="0.01"
                      value={editForm.flowrate}
                      onChange={(e) => handleInputChange('flowrate', parseFloat(e.target.value))}
                      className="edit-input"
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      step="0.01"
                      value={editForm.pressure}
                      onChange={(e) => handleInputChange('pressure', parseFloat(e.target.value))}
                      className="edit-input"
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      step="0.01"
                      value={editForm.temperature}
                      onChange={(e) => handleInputChange('temperature', parseFloat(e.target.value))}
                      className="edit-input"
                    />
                  </td>
                  <td>
                    <div className="action-cell">
                      <button className="btn-table btn-save" onClick={() => handleSaveClick(item)}>
                        ✓
                      </button>
                      <button className="btn-table btn-cancel-edit" onClick={handleCancelClick}>
                        ✕
                      </button>
                    </div>
                  </td>
                </>
              ) : (
                <>
                  <td>{item.name}</td>
                  <td>{item.type || item.equipment_type}</td>
                  <td>{parseFloat(item.flowrate).toFixed(2)}</td>
                  <td>{parseFloat(item.pressure).toFixed(2)}</td>
                  <td>{parseFloat(item.temperature).toFixed(2)}</td>
                  {editable && (
                    <td>
                      <div className="action-cell">
                        <button 
                          className="btn-table btn-edit" 
                          onClick={() => handleEditClick(item)}
                          title="Edit"
                        >
                          ✏️
                        </button>
                        <button 
                          className="btn-table btn-delete" 
                          onClick={() => onDelete && onDelete(item.id)}
                          title="Delete"
                        >
                          🗑️
                        </button>
                      </div>
                    </td>
                  )}
                </>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DataTable;
