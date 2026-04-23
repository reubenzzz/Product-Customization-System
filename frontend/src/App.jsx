import React, { useState, useEffect, useRef } from 'react';
import { UploadCloud, Download, X, Moon, Sun } from 'lucide-react';
import './index.css';

const API_BASE = 'https://highproduct-customization-system.onrender.com';

function App() {
  const [products, setProducts] = useState([]);
  const [mockups, setMockups] = useState({});
  const [isDragging, setIsDragging] = useState(false);
  
  // Theme state
  const [theme, setTheme] = useState('light');

  // File state
  const [selectedFile, setSelectedFile] = useState(null);
  const [imageSrc, setImageSrc] = useState(null);
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  
  // Advanced Pro Editor State
  const [scaleX, setScaleX] = useState(1.0);
  const [scaleY, setScaleY] = useState(1.0);
  const [rotation, setRotation] = useState(0);
  const [offsetX, setOffsetX] = useState(0);
  const [offsetY, setOffsetY] = useState(0);

  // Lightbox State
  const [lightboxImage, setLightboxImage] = useState(null);

  const fileInputRef = useRef(null);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  useEffect(() => {
    fetch(`${API_BASE}/api/products/`)
      .then(res => res.json())
      .then(data => {
        setProducts(data);
        const initialMockups = {};
        data.forEach(prod => {
          prod.views.forEach(view => {
            initialMockups[view.id] = { status: 'idle', url: null, baseImage: view.base_image };
          });
        });
        setMockups(initialMockups);
      })
      .catch(err => console.error("Error fetching products:", err));
  }, []);

  const toggleTheme = () => setTheme(theme === 'light' ? 'dark' : 'light');

  const onFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelection(e.target.files[0]);
      e.target.value = null;
    }
  };

  const onDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelection = (file) => {
    setSelectedFile(file);
    const reader = new FileReader();
    reader.onload = () => {
      setImageSrc(reader.result);
      // Reset editor controls
      setScaleX(1.0); setScaleY(1.0); setRotation(0); setOffsetX(0); setOffsetY(0);
      setIsEditorOpen(true);
    };
    reader.readAsDataURL(file);
  };

  const handleRenderMockups = async () => {
    setIsEditorOpen(false);

    setMockups(prev => {
      const loadingState = { ...prev };
      Object.keys(loadingState).forEach(id => {
        loadingState[id].status = 'loading';
      });
      return loadingState;
    });

    products.forEach(prod => {
      prod.views.forEach(async (view) => {
        const formData = new FormData();
        formData.append('product_view_id', view.id);
        formData.append('user_image', selectedFile);
        formData.append('scale_x', scaleX);
        formData.append('scale_y', scaleY);
        formData.append('rotation', rotation);
        formData.append('offset_x', offsetX);
        formData.append('offset_y', offsetY);

        try {
          const res = await fetch(`${API_BASE}/api/mockup/request/`, {
            method: 'POST',
            body: formData,
          });
          if (!res.ok) throw new Error("Backend error");
          const data = await res.json();
          pollStatus(view.id, data.task_id);
        } catch (err) {
          setMockups(prev => ({ ...prev, [view.id]: { ...prev[view.id], status: 'error' } }));
        }
      });
    });
  };

  const pollStatus = async (viewId, taskId) => {
    const check = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/mockup/status/${taskId}/`);
        if (!res.ok) throw new Error("Backend error");
        
        const data = await res.json();
        if (data.task_status === 'SUCCESS') {
          setMockups(prev => ({
            ...prev,
            [viewId]: { ...prev[viewId], status: 'success', url: `${API_BASE}${data.task_result.url}` }
          }));
        } else if (data.task_status === 'FAILURE') {
          setMockups(prev => ({ ...prev, [viewId]: { ...prev[viewId], status: 'error' } }));
        } else {
          setTimeout(check, 1000);
        }
      } catch (err) {
        setMockups(prev => ({ ...prev, [viewId]: { ...prev[viewId], status: 'error' } }));
      }
    };
    check();
  };

  return (
    <div className="container">
      <div className="header">
        <div>
          <h1 className="title">Magic Creator! ✨</h1>
          <p className="subtitle">Drop your drawing here to see it on everything!</p>
        </div>
        <button className="theme-toggle" onClick={toggleTheme}>
          {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
        </button>
      </div>

      <div 
        className={`dropzone ${isDragging ? 'active' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={onDrop}
        onClick={() => fileInputRef.current.click()}
      >
        <UploadCloud className="dropzone-icon" />
        <h2>Upload your artwork</h2>
        <p>Drag and drop or click to browse</p>
        <input type="file" className="file-input" ref={fileInputRef} onChange={onFileChange} accept="image/*" />
      </div>

      {isEditorOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-preview">
              <img 
                src={imageSrc} 
                className="preview-img"
                style={{ 
                  transform: `scaleX(${scaleX}) scaleY(${scaleY}) rotate(${rotation}deg) translate(${offsetX}px, ${offsetY}px)`,
                  maxWidth: '80%', maxHeight: '80%'
                }} 
                alt="Preview" 
              />
            </div>
            <div className="modal-controls">
              <h2>Pro Editor</h2>
              
              <div className="control-group">
                <label>Scale X (Zoom Width) <span>{scaleX}x</span></label>
                <input type="range" min="0.1" max="3" step="0.1" value={scaleX} onChange={(e) => setScaleX(e.target.value)} />
              </div>

              <div className="control-group">
                <label>Scale Y (Zoom Height) <span>{scaleY}x</span></label>
                <input type="range" min="0.1" max="3" step="0.1" value={scaleY} onChange={(e) => setScaleY(e.target.value)} />
              </div>

              <div className="control-group">
                <label>Rotation (Degrees) <span>{rotation}°</span></label>
                <input type="range" min="-180" max="180" step="1" value={rotation} onChange={(e) => setRotation(e.target.value)} />
              </div>

              <div className="control-group">
                <label>Offset X (Left/Right) <span>{offsetX}px</span></label>
                <input type="range" min="-200" max="200" step="5" value={offsetX} onChange={(e) => setOffsetX(e.target.value)} />
              </div>

              <div className="control-group">
                <label>Offset Y (Up/Down) <span>{offsetY}px</span></label>
                <input type="range" min="-200" max="200" step="5" value={offsetY} onChange={(e) => setOffsetY(e.target.value)} />
              </div>

              <div style={{ display: 'flex', gap: '1rem' }}>
                <button className="btn btn-primary" style={{ background: 'var(--border-color)', color: 'var(--text-dark)' }} onClick={() => setIsEditorOpen(false)}>Cancel</button>
                <button className="btn btn-primary" onClick={handleRenderMockups}>Render 3D Mockups</button>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="gallery">
        {products.map(prod => (
          prod.views.map(view => {
            const state = mockups[view.id];
            if (!state) return null;

            return (
              <div key={view.id} className="product-card" onClick={() => state.status === 'success' && setLightboxImage(state.url)}>
                <h3>{prod.name} - {view.name}</h3>
                <div className="image-container">
                  {state.status === 'idle' && <img src={`${API_BASE}${state.baseImage}`} alt={prod.name} style={{ opacity: 0.5 }} />}
                  {state.status === 'loading' && <div className="loader"></div>}
                  {state.status === 'success' && <img src={state.url} alt={`Mockup for ${prod.name}`} />}
                  {state.status === 'error' && <p>Error rendering.</p>}
                </div>
              </div>
            );
          })
        ))}
      </div>

      {lightboxImage && (
        <div className="lightbox" onClick={() => setLightboxImage(null)}>
          <button className="btn-close" onClick={() => setLightboxImage(null)}><X /></button>
          <img src={lightboxImage} alt="Fullscreen Mockup" onClick={(e) => e.stopPropagation()} />
          <div className="lightbox-actions" onClick={(e) => e.stopPropagation()}>
            <a href={lightboxImage} download="My_Custom_Mockup.png" className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Download size={18} /> Download High-Res
            </a>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
