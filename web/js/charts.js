/* ==========================================================================
   Stratoterra — Charts (Canvas Sparklines + Radar)
   ========================================================================== */

var Charts = {
  drawSparkline: function(canvas, dataPoints, color) {
    if (!canvas || !dataPoints || dataPoints.length < 2) return;
    var ctx = canvas.getContext('2d');
    var w = canvas.width;
    var h = canvas.height;
    var dpr = window.devicePixelRatio || 1;

    canvas.width = w * dpr;
    canvas.height = h * dpr;
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';
    ctx.scale(dpr, dpr);

    var values = dataPoints.map(function(d) { return typeof d === 'number' ? d : d.value; });
    var min = Math.min.apply(null, values);
    var max = Math.max.apply(null, values);
    var range = max - min || 1;
    var pad = 2;

    ctx.clearRect(0, 0, w, h);
    ctx.beginPath();
    ctx.strokeStyle = color || '#6ca6ff';
    ctx.lineWidth = 1.5;
    ctx.lineJoin = 'round';

    for (var i = 0; i < values.length; i++) {
      var x = pad + (i / (values.length - 1)) * (w - 2 * pad);
      var y = h - pad - ((values[i] - min) / range) * (h - 2 * pad);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Fill area under line
    ctx.lineTo(pad + ((values.length - 1) / (values.length - 1)) * (w - 2 * pad), h - pad);
    ctx.lineTo(pad, h - pad);
    ctx.closePath();
    ctx.fillStyle = color ? color.replace(')', ', 0.1)').replace('rgb', 'rgba') : 'rgba(108, 166, 255, 0.1)';
    ctx.fill();

    // End dot
    var lastX = pad + ((values.length - 1) / (values.length - 1)) * (w - 2 * pad);
    var lastY = h - pad - ((values[values.length - 1] - min) / range) * (h - 2 * pad);
    ctx.beginPath();
    ctx.arc(lastX, lastY, 2, 0, Math.PI * 2);
    ctx.fillStyle = color || '#6ca6ff';
    ctx.fill();
  },

  drawRadarChart: function(canvas, datasets, labels) {
    if (!canvas || !datasets || !labels) return;
    var ctx = canvas.getContext('2d');
    var w = canvas.width;
    var h = canvas.height;
    var dpr = window.devicePixelRatio || 1;

    canvas.width = w * dpr;
    canvas.height = h * dpr;
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';
    ctx.scale(dpr, dpr);

    var cx = w / 2;
    var cy = h / 2;
    var radius = Math.min(cx, cy) - 40;
    var numAxes = labels.length;
    var angleStep = (2 * Math.PI) / numAxes;
    var startAngle = -Math.PI / 2;

    ctx.clearRect(0, 0, w, h);

    // Draw grid circles
    var gridLevels = 5;
    for (var level = 1; level <= gridLevels; level++) {
      var r = (radius / gridLevels) * level;
      ctx.beginPath();
      ctx.strokeStyle = 'rgba(100, 100, 180, 0.15)';
      ctx.lineWidth = 1;
      for (var i = 0; i <= numAxes; i++) {
        var angle = startAngle + i * angleStep;
        var x = cx + r * Math.cos(angle);
        var y = cy + r * Math.sin(angle);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
    }

    // Draw axes and labels
    ctx.font = '11px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    for (var i = 0; i < numAxes; i++) {
      var angle = startAngle + i * angleStep;
      var axisX = cx + radius * Math.cos(angle);
      var axisY = cy + radius * Math.sin(angle);

      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(axisX, axisY);
      ctx.strokeStyle = 'rgba(100, 100, 180, 0.2)';
      ctx.lineWidth = 1;
      ctx.stroke();

      // Label
      var labelX = cx + (radius + 24) * Math.cos(angle);
      var labelY = cy + (radius + 24) * Math.sin(angle);
      ctx.fillStyle = '#9898b8';
      ctx.fillText(labels[i], labelX, labelY);
    }

    // Draw datasets
    var colors = ['#6ca6ff', '#ff6b6b', '#ffd54f', '#69f0ae', '#ab47bc'];
    datasets.forEach(function(dataset, di) {
      var color = colors[di % colors.length];
      ctx.beginPath();
      for (var i = 0; i < numAxes; i++) {
        var val = Math.max(0, Math.min(1, dataset.values[i] || 0));
        var angle = startAngle + i * angleStep;
        var x = cx + radius * val * Math.cos(angle);
        var y = cy + radius * val * Math.sin(angle);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.closePath();
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.stroke();
      ctx.fillStyle = color.replace(')', ', 0.15)').replace('#', 'rgba(');

      // Convert hex to rgba for fill
      var r = parseInt(color.slice(1, 3), 16);
      var g = parseInt(color.slice(3, 5), 16);
      var b = parseInt(color.slice(5, 7), 16);
      ctx.fillStyle = 'rgba(' + r + ',' + g + ',' + b + ', 0.12)';
      ctx.fill();

      // Data points
      for (var i = 0; i < numAxes; i++) {
        var val = Math.max(0, Math.min(1, dataset.values[i] || 0));
        var angle = startAngle + i * angleStep;
        var x = cx + radius * val * Math.cos(angle);
        var y = cy + radius * val * Math.sin(angle);
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
      }
    });
  }
};
