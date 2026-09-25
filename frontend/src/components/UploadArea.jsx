import { useRef, useState } from 'react'

const ACCEPTED = ['image/jpeg', 'image/png', 'application/pdf']

export default function UploadArea({ file, onFileSelected, onRemove, uploadProgress }) {
  const inputRef = useRef(null)
  const [dragOver, setDragOver] = useState(false)

  function handleFiles(fileList) {
    const picked = fileList[0]
    if (!picked) return
    if (!ACCEPTED.includes(picked.type)) {
      alert('Please upload a JPG, PNG, or PDF file.')
      return
    }
    onFileSelected(picked)
  }

  if (file) {
    const isUploading = uploadProgress !== null && uploadProgress < 100
    return (
      <div>
        <div className="file-chip">
          <div>
            <div className="name">{file.name}</div>
            <div className="meta">{(file.size / 1024).toFixed(0)} KB &middot; {file.type.split('/')[1]?.toUpperCase()}</div>
          </div>
          {!isUploading && <button onClick={onRemove}>Remove</button>}
        </div>
        {isUploading && (
          <div className="progress-track">
            <div className="progress-fill" style={{ width: `${uploadProgress}%` }} />
          </div>
        )}
      </div>
    )
  }

  return (
    <div
      className={`upload-area ${dragOver ? 'dragover' : ''}`}
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault()
        setDragOver(false)
        handleFiles(e.dataTransfer.files)
      }}
    >
      <div className="headline">Drop your report here, or click to browse</div>
      <div className="hint">JPG, PNG, or PDF &middot; up to 15MB</div>
      <input
        ref={inputRef}
        type="file"
        accept=".jpg,.jpeg,.png,.pdf"
        onChange={(e) => handleFiles(e.target.files)}
      />
    </div>
  )
}
