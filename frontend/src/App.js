import { useState } from 'react';

function App() {
  const [url, setUrl] = useState('');
  const [isConverting, setIsConverting] = useState(false);

  const handleConvert = async () => {
    setIsConverting(true);

    try {
      const response = await fetch('http://127.0.0.1:5000/convert', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ youtubeUrl: url }),
      });

      const data = await response.json();

      if (response.ok && data.downloadUrl) {
        // Open the pre-signed URL in a new tab
        window.open(data.downloadUrl, '_blank');
      } else {
        alert('Conversion failed: ' + data.error);
      }
    } catch (error) {
      alert('An error occurred: ' + error.message);
    } finally {
      setIsConverting(false);
    }
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '50px' }}>
      <h1>Project MP3: YouTube to MP3 Converter</h1>
      <input
        type="text"
        placeholder="Enter YouTube URL"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        style={{ width: '300px', padding: '10px', margin: '10px' }}
      />
      <button
        onClick={handleConvert}
        disabled={isConverting || !url}
        style={{
          padding: '10px 20px',
          backgroundColor: '#007BFF',
          color: 'white',
          border: 'none',
          cursor: 'pointer',
        }}
      >
        {isConverting ? 'Converting...' : 'Convert'}
      </button>
    </div>
  );
}

export default App;
