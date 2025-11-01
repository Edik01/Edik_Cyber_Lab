import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./style.css";

const el = document.getElementById("app");
if (!el) throw new Error("Root element #app not found");
createRoot(el).render(<App />);

