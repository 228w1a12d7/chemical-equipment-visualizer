import React, { useState, useRef } from 'react';
import { dataAPI } from '../../services/api';
import { toast } from 'react-toastify';

const FileUpload = ({ onUploadSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFileSelect = (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFile = async (file) => {
    if (!file.name.endsWith('.csv')) {
      toast.error('Please upload a CSV file');
      return;
    }

    setUploading(true);

    try {
      const response = await dataAPI.uploadCSV(file);
      toast.success('File uploaded successfully!');
      if (onUploadSuccess) {
        onUploadSuccess(response.data);
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Upload failed. Please try again.';
      toast.error(errorMessage);
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div
      className={`upload-area ${isDragging ? 'dragging' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={handleClick}
    >
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileSelect}
        accept=".csv"
      />
      
      <div className="upload-icon">📁</div>
      
      {uploading ? (
        <>
          <h4>Uploading...</h4>
          <div className="spinner" style={{ margin: '20px auto' }}></div>
        </>
      ) : (
        <>
          <h4>Drag & Drop your CSV file here</h4>
          <p>or click to browse</p>
          <p style={{ marginTop: '15px', fontSize: '12px', color: '#aaa' }}>
            Required columns: Equipment Name, Type, Flowrate, Pressure, Temperature
          </p>
        </>
      )}
    </div>
  );
};

export default FileUpload;
