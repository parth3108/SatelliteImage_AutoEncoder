import React, { useState } from 'react';

function ImageUpload({ onImageUpload, preview }) {
  const [isDragging, setIsDragging] = useState(false);

  // Handle drag events
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      onImageUpload(file);
    }
  };

  // Handle file selection through the input
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      onImageUpload(file);
    }
  };

  return (
    <div
      className={`upload-box ${isDragging ? 'dragging' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      style={{
        border: isDragging ? '2px solid #4285F4' : '2px dashed #ccc',
        width: '300px',
        height: '200px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        cursor: 'pointer',
        marginBottom: '20px',
        borderRadius: '8px',
        transition: 'border 0.3s ease-in-out',
        position: 'relative', // Set position to relative for proper containment
      }}
    >
      {/* File input only covers the area of the upload box */}
      <input
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        style={{
          opacity: 0,
          width: '100%',
          height: '100%',
          position: 'absolute',
          top: 0,
          left: 0,
          cursor: 'pointer',
        }}
      />
      {preview ? (
        <img src={preview} alt="Uploaded" style={{ maxWidth: '100%', maxHeight: '100%', borderRadius: '8px' }} />
      ) : (
        <div>
          <p>Drag & drop an image here, or click to browse</p>
        </div>
      )}
    </div>
  );
}

export default ImageUpload;
