import React from "react";
import { frameUrl } from "../api";

export default function Feed({ filename }) {
  if (!filename) {
    return <div className="feed placeholder">No frame yet</div>;
  }

  return (
    <div className="feed">
      <img src={frameUrl(filename)} alt={filename} />
      <div className="caption">{filename}</div>
    </div>
  );
}

