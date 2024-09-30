import React from 'react';

function StatisticsGraph({ graph }) {
  return (
    <div className="statistics-graph">
      <h3>Statistics Graph</h3>
      <img src={`data:image/png;base64,${graph}`} alt="Statistics Graph" />
    </div>
  );
}

export default StatisticsGraph;
