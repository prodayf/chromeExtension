import React, { useState } from "react";
import "./App.css"; // Importa el archivo CSS

function App() {
  const [url, setUrl] = useState("");
  const [response, setResponse] = useState(null); // Estado para almacenar la respuesta de la API
  const [error, setError] = useState(null); // Estado para manejar errores
  const [isLoading, setIsLoading] = useState(false); // Estado para manejar la carga

  // Función para manejar el cambio en el input
  const handleInputChange = (event) => {
    setUrl(event.target.value);
  };

  // Función para manejar el clic en el botón
  const handleSubmit = async () => {
    if (!url) {
      alert("Por favor, ingresa una URL válida.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setResponse(null);

    const controller = new AbortController();
    const signal = controller.signal;
    const timeout = setTimeout(() => controller.abort(), 30000); // 30 segundos de espera

    try {
      const apiUrl = `http://127.0.0.1:8000/analyze_youtube/?youtube_url=${url}`;
      const res = await fetch(apiUrl, { signal });

      if (!res.ok) {
        throw new Error("Error al hacer la petición a la API");
      }

      const data = await res.json();
      setResponse(data);
    } catch (err) {
      if (err.name === "AbortError") {
        setError("Tiempo de espera agotado. Intenta de nuevo.");
      } else {
        setError(err.message);
      }
    } finally {
      clearTimeout(timeout);
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>ChromeExtension</h1>
      <h3>Paste LINK</h3>
      <input
        type="text"
        value={url}
        onChange={handleInputChange}
        placeholder="Ingresa una URL de YouTube"
      />

      {response && (
        <div className="response">
          <p><strong>Tonality:</strong> {response.tonality}</p>
          <p><strong>Mode:</strong> {response.mode}</p>
          <p><strong>BPM:</strong> {response.bpm}</p>
        </div>
      )}

      {error && <p className="error">Error: {error}</p>}
      {isLoading && <p className="loading">Cargando...</p>}

      <button onClick={handleSubmit} disabled={isLoading}>
        {isLoading ? "Procesando..." : "Submit"}
      </button>
    </div>
  );
}

export default App;
