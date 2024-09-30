import React from 'react';

function MetricsTable({ metrics }) {
  return (
    <div className="metrics-table">
      <h3>PSNR & SSIM Comparison</h3>
      <table>
        <thead>
          <tr>
            <th>Compression Technique</th>
            <th>PSNR</th>
            <th>SSIM</th>
          </tr>
        </thead>
        <tbody>
          {metrics.map((metric, index) => (
            <tr key={index}>
              <td>{metric.technique}</td>
              <td>{metric.psnr}</td>
              <td>{metric.ssim}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default MetricsTable;
