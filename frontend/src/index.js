import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import "./debug-env.js"; // Import debug logging

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
