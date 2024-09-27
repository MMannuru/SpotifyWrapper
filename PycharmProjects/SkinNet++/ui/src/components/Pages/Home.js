import React, { useState, useRef } from 'react';
import './Home.css';

export const Home = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [showText, setShowText] = useState(true);
  const [showPreview, setShowPreview] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const videoRef = useRef(null);

  const startCamera = () => {
    navigator.mediaDevices
      .getUserMedia({ video: true })
      .then((stream) => {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      })
      .catch((error) => {
        console.error('Error accessing the camera:', error);
      });
  };

  const captureImage = () => {
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
    const imageUrl = canvas.toDataURL('image/jpeg');
    setSelectedImage(imageUrl);
    setShowText(false);
    setShowPreview(true);
  };

  const handleImageChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const imageUrl = URL.createObjectURL(file);
      setSelectedImage(imageUrl);
      setShowText(false);
      setShowPreview(true);
    } else {
      setSelectedImage(null);
      setShowText(true);
      setShowPreview(false);
    }
    alert(file);
    setSelectedImage(file);
  };

  const sendImageToAPI = () => {
    if (selectedImage) {
      fetch(selectedImage)
        .then((response) => response.blob()) // Convert the selectedImage to a Blob
        .then((blob) => {
          const reader = new FileReader();
  
          reader.onload = (event) => {
            const imageBytes = new Uint8Array(event.target.result);
            fetch('http://127.0.0.1:5000/predict', {
              method: 'POST',
              body: imageBytes,
            })
              .then((response) => response.json())
              .then((data) => {
                console.log(JSON.stringify(data));
                alert(data.predicted_class);
              })
              .catch((error) => {
                console.error('Error:', error);
              });
          };
  
          // Read the image Blob as an ArrayBuffer
          reader.readAsArrayBuffer(blob);
        })
        .catch((error) => {
          console.error('Error:', error);
        });
    }
  };
  

  const uploadButtonClick = () => {
    setShowUpload(true);
    sendImageToAPI();
  };

  return (
    <>
      <div className="container">
        <div className="left-content">
          <h1>Welcome to Dermalize</h1>
          <div className="center-content">
            <label htmlFor="image-upload-input" className="btn">
              Choose File
              <input
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                style={{ display: 'none' }}
                id="image-upload-input"
              />
            </label>
          </div>
          <div className="center-content">
            <button className="btn" onClick={startCamera}>
              Use Camera
            </button>
            <button className="btn" onClick={captureImage}>
              Capture Image
            </button>
          </div>
        </div>
        {showPreview && (
          <div>
            <h1>Preview:</h1>
            <img
              src={selectedImage}
              alt="Uploaded"
              style={{
                maxWidth: '100px',
                height: 'auto',
              }}
            />
            <button className="btn" onClick={uploadButtonClick}>
              Upload
            </button>
          </div>
        )}
        {showUpload && (
          <div className="right-content">
            <h1>Uploaded:</h1>
            <img
              src={selectedImage}
              style={{
                maxWidth: '100px',
                height: 'auto',
              }}
            />
          </div>
        )}
      </div>
      {showText && (
        <div className="container-text">
          <h2>
            {/* Your existing text */}
          </h2>
        </div>
      )}
      <video ref={videoRef} style={{ display: 'none' }}></video>
    </>
  );
};
