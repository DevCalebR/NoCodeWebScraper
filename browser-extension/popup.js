// Browser extension popup logic - Coming soon!
let isRecording = false;

document.getElementById('toggle-recording').addEventListener('click', function() {
  if (!isRecording) {
    isRecording = true;
    this.textContent = '⏹ Stop Recording';
    this.className = 'btn-stop';
    document.getElementById('status').className = 'status recording';
    document.getElementById('status-text').innerHTML = '<span style="color: #ef4444;">● Recording...</span>';
  } else {
    isRecording = false;
    this.textContent = '● Start Recording';
    this.className = 'btn-start';
    document.getElementById('status').className = 'status';
    document.getElementById('status-text').textContent = 'Recording stopped';
  }
});

console.log('ScraperPro Visual Recorder - Popup loaded');
