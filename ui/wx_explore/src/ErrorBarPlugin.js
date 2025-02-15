import Chart from 'chart.js';

const ErrorBarPlugin = {
  id: 'error-bars',
  afterDatasetsDraw: (chart) => {
    const ctx = chart.ctx;

    chart.data.datasets.forEach((dataset, i) => {
      if (!dataset.errorBars || !dataset.errorBars.show || !dataset.errorBarData) {
        return;
      }

      const meta = chart.getDatasetMeta(i);

      dataset.data.forEach((point, j) => {
        const errorData = dataset.errorBarData[j];
        if (!errorData) return;

        const { x, y } = meta.data[j].getCenterPoint();
        const yScale = chart.scales[meta.yAxisID];

        // Save current drawing state
        ctx.save();

        // Error bar styling
        ctx.strokeStyle = dataset.errorBars.color || dataset.borderColor;
        ctx.lineWidth = dataset.errorBars.lineWidth || 1;

        // Draw vertical error bar
        const yPlus = yScale.getPixelForValue(point.y + errorData.plus);
        const yMinus = yScale.getPixelForValue(point.y - errorData.minus);
        const tipWidth = dataset.errorBars.tipWidth || 6;

        // Vertical line
        ctx.beginPath();
        ctx.moveTo(x, yPlus);
        ctx.lineTo(x, yMinus);
        ctx.stroke();

        // Top horizontal tip
        ctx.beginPath();
        ctx.moveTo(x - tipWidth / 2, yPlus);
        ctx.lineTo(x + tipWidth / 2, yPlus);
        ctx.stroke();

        // Bottom horizontal tip
        ctx.beginPath();
        ctx.moveTo(x - tipWidth / 2, yMinus);
        ctx.lineTo(x + tipWidth / 2, yMinus);
        ctx.stroke();

        // Restore drawing state
        ctx.restore();
      });
    });
  }
};

// Register the plugin
Chart.plugins.register(ErrorBarPlugin);

export default ErrorBarPlugin;