import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import ImageUpload from './components/ImageUpload';
import CompressionOptions from './components/CompressionOptions';
import ProcessedImage from './components/ProcessedImage';
import MetricsTable from './components/MetricsTable';
import StatisticsGraph from './components/StatisticsGraph';
import NoiseVisualization from './components/NoiseVisualization';

function App() {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [compressionType, setCompressionType] = useState('JPEG');
  const [quality, setQuality] = useState(50);
  const [results, setResults] = useState(null);

  const handleImageUpload = (file) => {
    setImage(file);

    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result);
    };
    reader.readAsDataURL(file);
  };

  const processImage = async () => {
    const formData = new FormData();
    formData.append('image', image);
    formData.append('compressionType', compressionType);
    formData.append('quality', quality);

    try {
      const response = await axios.post('http://localhost:5000/process-image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResults(response.data);
    } catch (error) {
      console.error('Error processing image:', error);
    }
  };

  return (
    <div className="App">
      <ImageUpload onImageUpload={handleImageUpload} preview={preview} />
      <CompressionOptions
        compressionType={compressionType}
        setCompressionType={setCompressionType}
        quality={quality}
        setQuality={setQuality}
      />
      <button onClick={processImage}>Process Image</button>
      
      {results && (
        <div className="results">
          <ProcessedImage images={results.compressed_images} />
          <StatisticsGraph graph={results.graph} />
          <MetricsTable metrics={results.metrics} />
          <NoiseVisualization noise={results.noise} />
        </div>
      )}
    </div>
  );
}

export default App;
