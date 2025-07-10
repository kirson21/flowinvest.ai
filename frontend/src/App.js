import React from "react";
import "./App.css";
import { BrowserRouter } from "react-router-dom";
import { AppProvider } from "./contexts/AppContext";
import MainApp from "./components/MainApp";

function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <div className="App">
          <MainApp />
        </div>
      </BrowserRouter>
    </AppProvider>
  );
}

export default App;
