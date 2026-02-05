import React from 'react';
import { Pie, Bar, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const chartColors = [
  '#667eea',
  '#764ba2',
  '#f093fb',
  '#f5576c',
  '#4facfe',
  '#00f2fe',
  '#43e97b',
  '#38f9d7',
  '#fa709a',
  '#fee140',
];

// Equipment Type Distribution - Pie Chart
export const TypeDistributionChart = ({ data }) => {
  if (!data || Object.keys(data).length === 0) {
    return <div className="empty-state"><p>No data available</p></div>;
  }

  const chartData = {
    labels: Object.keys(data),
    datasets: [
      {
        data: Object.values(data),
        backgroundColor: chartColors.slice(0, Object.keys(data).length),
        borderColor: 'white',
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: 'right',
        labels: {
          font: {
            family: 'Inter',
            size: 12,
          },
          padding: 15,
        },
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const total = context.dataset.data.reduce((a, b) => a + b, 0);
            const percentage = ((context.raw / total) * 100).toFixed(1);
            return `${context.label}: ${context.raw} (${percentage}%)`;
          },
        },
      },
    },
  };

  return <Pie data={chartData} options={options} />;
};

// Parameter Comparison - Bar Chart
export const ParameterComparisonChart = ({ data }) => {
  if (!data || data.length === 0) {
    return <div className="empty-state"><p>No data available</p></div>;
  }

  // Group by type and calculate averages
  const typeGroups = {};
  data.forEach(item => {
    const type = item.type || item.equipment_type;
    if (!typeGroups[type]) {
      typeGroups[type] = { flowrate: [], pressure: [], temperature: [] };
    }
    typeGroups[type].flowrate.push(parseFloat(item.flowrate));
    typeGroups[type].pressure.push(parseFloat(item.pressure));
    typeGroups[type].temperature.push(parseFloat(item.temperature));
  });

  const labels = Object.keys(typeGroups);
  const avgFlowrate = labels.map(type => {
    const vals = typeGroups[type].flowrate;
    return vals.reduce((a, b) => a + b, 0) / vals.length;
  });
  const avgPressure = labels.map(type => {
    const vals = typeGroups[type].pressure;
    return vals.reduce((a, b) => a + b, 0) / vals.length;
  });
  const avgTemperature = labels.map(type => {
    const vals = typeGroups[type].temperature;
    return vals.reduce((a, b) => a + b, 0) / vals.length;
  });

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Avg Flowrate',
        data: avgFlowrate,
        backgroundColor: '#667eea',
        borderRadius: 4,
      },
      {
        label: 'Avg Pressure',
        data: avgPressure,
        backgroundColor: '#764ba2',
        borderRadius: 4,
      },
      {
        label: 'Avg Temperature',
        data: avgTemperature,
        backgroundColor: '#f5576c',
        borderRadius: 4,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          font: {
            family: 'Inter',
            size: 12,
          },
        },
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          font: {
            family: 'Inter',
            size: 11,
          },
        },
      },
      y: {
        beginAtZero: true,
        grid: {
          color: '#f0f0f0',
        },
        ticks: {
          font: {
            family: 'Inter',
            size: 11,
          },
        },
      },
    },
  };

  return <Bar data={chartData} options={options} />;
};

// Individual Equipment Parameters - Line Chart
export const EquipmentLineChart = ({ data, parameter }) => {
  if (!data || data.length === 0) {
    return <div className="empty-state"><p>No data available</p></div>;
  }

  const sortedData = [...data].sort((a, b) => 
    parseFloat(b[parameter]) - parseFloat(a[parameter])
  ).slice(0, 15); // Top 15 for readability

  const chartData = {
    labels: sortedData.map(item => item.name),
    datasets: [
      {
        label: parameter.charAt(0).toUpperCase() + parameter.slice(1),
        data: sortedData.map(item => parseFloat(item[parameter])),
        borderColor: '#667eea',
        backgroundColor: 'rgba(102, 126, 234, 0.1)',
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#667eea',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 5,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          font: {
            family: 'Inter',
            size: 10,
          },
          maxRotation: 45,
          minRotation: 45,
        },
      },
      y: {
        beginAtZero: true,
        grid: {
          color: '#f0f0f0',
        },
        ticks: {
          font: {
            family: 'Inter',
            size: 11,
          },
        },
      },
    },
  };

  return <Line data={chartData} options={options} />;
};

// Type Count Bar Chart
export const TypeCountChart = ({ data }) => {
  if (!data || Object.keys(data).length === 0) {
    return <div className="empty-state"><p>No data available</p></div>;
  }

  const chartData = {
    labels: Object.keys(data),
    datasets: [
      {
        label: 'Equipment Count',
        data: Object.values(data),
        backgroundColor: chartColors.slice(0, Object.keys(data).length),
        borderRadius: 8,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          font: {
            family: 'Inter',
            size: 11,
          },
        },
      },
      y: {
        beginAtZero: true,
        grid: {
          color: '#f0f0f0',
        },
        ticks: {
          font: {
            family: 'Inter',
            size: 11,
          },
          stepSize: 1,
        },
      },
    },
  };

  return <Bar data={chartData} options={options} />;
};
