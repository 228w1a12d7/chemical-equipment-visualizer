import React from 'react';

const DataTable = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="empty-state">
        <h3>No data available</h3>
        <p>Upload a CSV file to see the equipment data here</p>
      </div>
    );
  }

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
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr key={index}>
              <td>{item.name}</td>
              <td>{item.type || item.equipment_type}</td>
              <td>{parseFloat(item.flowrate).toFixed(2)}</td>
              <td>{parseFloat(item.pressure).toFixed(2)}</td>
              <td>{parseFloat(item.temperature).toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DataTable;
