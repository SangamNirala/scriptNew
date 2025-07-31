import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";

// Import ResizeObserver polyfill to prevent loop errors
import "./utils/resizeObserverPolyfill";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
