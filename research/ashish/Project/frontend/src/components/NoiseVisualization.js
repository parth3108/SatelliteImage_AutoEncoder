import React from 'react';

function NoiseVisualization({ noise }) {
  return (
    <div className="noise-visualization">
      <h3>Noise Visualization</h3>
      <img src={`data:image/png;base64,${noise}`} alt="Noise Visualization" />
    </div>
  );
}

export default NoiseVisualization;
