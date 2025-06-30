import React, { useState, useEffect } from 'react';
import './MainLayout.css';

const MainLayout = ({ children, className }) => {
  const [schoolConfig, setSchoolConfig] = useState({
    name: "Nombre del Colegio (Cargando...)",
    logo: null, // Inicialmente no hay logo
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSchoolConfig = async () => {
      try {
        // Asumimos que la API está en /api/core/school-configurations/
        // Y que solo hay una configuración (o tomamos la primera)
        const response = await fetch('/api/core/school-configurations/');
        if (!response.ok) {
          throw new Error(`Error HTTP: ${response.status}`);
        }
        const data = await response.json();
        if (data && data.length > 0) {
          // Asumimos que la API devuelve una lista y tomamos el primer elemento.
          // Si la API devuelve un solo objeto, esto necesitará ajuste.
          setSchoolConfig({
            name: data[0].name || "Nombre del Colegio",
            logo: data[0].logo || null, // data[0].logo debería ser la URL completa si está bien configurado
          });
        } else if (data && !Array.isArray(data)) { // Si la API devuelve un solo objeto directamente
          setSchoolConfig({
            name: data.name || "Nombre del Colegio",
            logo: data.logo || null,
          });
        }
        else {
          setSchoolConfig({ name: "Nombre del Colegio (Por defecto)", logo: null });
        }
      } catch (e) {
        console.error("Error al cargar la configuración del colegio:", e);
        setError(e.message);
        // Mantener un nombre por defecto en caso de error
        setSchoolConfig(prevConfig => ({ ...prevConfig, name: "Nombre del Colegio (Error)" }));
      } finally {
        setLoading(false);
      }
    };

    fetchSchoolConfig();
  }, []); // El array vacío asegura que se ejecute solo una vez

  return (
    <div className={`main-layout ${className || ''}`}>
      <header className="main-header">
        <div className="logo-container">
          {loading && <div className="school-logo-placeholder">Cargando Logo...</div>}
          {!loading && schoolConfig.logo && (
            <img src={schoolConfig.logo} alt={`${schoolConfig.name} Logo`} className="school-logo" />
          )}
          {!loading && !schoolConfig.logo && (
            <div className="school-logo-placeholder">Logo</div>
          )}
          <h1>{schoolConfig.name}</h1>
        </div>
        <div className="banner-container">
          {/* El banner puede ser un color, una imagen de fondo, o más complejo */}
          <p>Banner Principal de la Institución</p>
        </div>
      </header>

      <main className="main-content-area">
        {children}
      </main>

      <footer className="main-footer">
        <p>© {new Date().getFullYear()} {schoolConfig.name}. Todos los derechos reservados.</p>
        <div className="social-media-links">
          {error && <p style={{color: 'red'}}>Error cargando config: {error}</p> }
          <a href="https://facebook.com" target="_blank" rel="noopener noreferrer">Facebook</a>
          <a href="https://twitter.com" target="_blank" rel="noopener noreferrer">Twitter</a>
          <a href="https://instagram.com" target="_blank" rel="noopener noreferrer">Instagram</a>
          {/* Añadir más redes si es necesario */}
        </div>
      </footer>
    </div>
  );
};

export default MainLayout;
