function createAttendanceChart(dates, attendanceCounts) {
  var ctx = document.getElementById('attendanceChart').getContext('2d');
  var chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: dates,
      datasets: [{
        label: 'Attendance',
        data: attendanceCounts,
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
        pointRadius: 3,
        pointBackgroundColor: 'rgba(54, 162, 235, 1)',
        pointBorderColor: 'rgba(255, 255, 255, 1)',
        pointHoverRadius: 5,
        pointHoverBackgroundColor: 'rgba(54, 162, 235, 1)',
        pointHoverBorderColor: 'rgba(255, 255, 255, 1)',
        pointHitRadius: 10,
        pointBorderWidth: 2,
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
          stepSize: 1,
        }
      }
    }
  });
}