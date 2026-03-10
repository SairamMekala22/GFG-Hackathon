import { Upload } from "lucide-react";
import { useRef, useState } from "react";

function FileUpload({ onUpload, uploading }) {
  const inputRef = useRef(null);
  const [fileName, setFileName] = useState("");

  const handleChange = async (event) => {
    const [file] = event.target.files || [];
    if (!file) {
      return;
    }

    setFileName(file.name);
    await onUpload(file);
  };

  return (
    <div className="rounded-3xl border border-dashed border-white/15 bg-white/5 p-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm font-semibold text-slate-100">CSV Upload</p>
          <p className="text-xs text-slate-400">
            Add a dataset and the backend will auto-register it in SQLite.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            disabled={uploading}
            className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/10 px-4 py-2 text-sm font-medium text-slate-100 transition hover:bg-white/20 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <Upload size={16} />
            {uploading ? "Uploading..." : "Upload CSV"}
          </button>
          {fileName && <span className="text-xs text-slate-400">{fileName}</span>}
        </div>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept=".csv"
        className="hidden"
        onChange={handleChange}
      />
    </div>
  );
}

export default FileUpload;
