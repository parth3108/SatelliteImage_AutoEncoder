import React from 'react';

function ProcessedImage({ images }) {
  return (
    <div className="compressed-images">
      <h3>Compressed Images</h3>
      {images.map((img, index) => (
        <div key={index}>
          <img
            src={`data:image/jpeg;base64,${img}`}
            alt={`Compressed ${index}`}
            style={{ width: '50px', height: '50px' }}
          />
          <a href={`data:image/jpeg;base64,${img}`} download={`compressed_${index}.jpg`}>
            Download
          </a>
        </div>
      ))}
    </div>
  );
}

export default ProcessedImage;
