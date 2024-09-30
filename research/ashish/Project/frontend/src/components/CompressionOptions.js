import React from 'react';

function CompressionOptions({ compressionType, setCompressionType, quality, setQuality }) {
  return (
    <div className="compression-options">
      <label>Compression Type: </label>
      <select onChange={(e) => setCompressionType(e.target.value)} value={compressionType}>
        <option value="JPEG">JPEG</option>
        <option value="PNG">PNG</option>
        <option value="WebP">WebP</option>
        <option value="Custom">Custom</option>
      </select>

      {compressionType === 'JPEG' && (
        <div>
          <label>Quality (1-100): </label>
          <input type="range" min="1" max="100" value={quality} onChange={(e) => setQuality(e.target.value)} />
          <span>{quality}</span>
        </div>
      )}
    </div>
  );
}

export default CompressionOptions;
