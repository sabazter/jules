import React, { useState, useEffect } from 'react';

function NivelEducativoPage() {
  const [niveles, setNiveles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchNiveles = async () => {
      try {
        // Ajusta la URL si tu API está en un puerto o dominio diferente durante el desarrollo
        const response = await fetch('/api/core/levels/');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setNiveles(data);
      } catch (e) {
        setError(e.message);
        console.error("Error fetching niveles:", e);
      } finally {
        setLoading(false);
      }
    };

    fetchNiveles();
  }, []); // El array vacío asegura que useEffect se ejecute solo una vez (al montar)

  if (loading) {
    return <p>Cargando niveles educativos...</p>;
  }

  if (error) {
    return (
      <div>
        <p>Error al cargar los niveles educativos: {error}</p>
        <p>
          Asegúrate de que el servidor de Django esté corriendo y que la API
          en <code>/api/core/levels/</code> sea accesible.
        </p>
        <p>
          También, si estás corriendo el frontend (React) y el backend (Django) en puertos diferentes,
          necesitarás configurar CORS en Django o usar un proxy en el servidor de desarrollo de React.
        </p>
      </div>
    );
  }

  return (
    <div className="nivel-educativo-page">
      <h1>Niveles Educativos</h1>
      {niveles.length > 0 ? (
        <ul>
          {niveles.map(nivel => (
            <li key={nivel.id}>
              {nivel.name_display || nivel.name} (ID: {nivel.id}, Valor crudo: {nivel.name})
            </li>
          ))}
        </ul>
      ) : (
        <p>No hay niveles educativos para mostrar.</p>
      )}
    </div>
  );
}

export default NivelEducativoPage;
