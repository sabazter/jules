import React, { useState, useEffect, useCallback } from 'react';
import './SchoolConfigurationPage.css'; // Crearemos este archivo para estilos

function SchoolConfigurationPage() {
  const [config, setConfig] = useState(null);
  const [configId, setConfigId] = useState(null); // Para saber qué ID actualizar
  const [schoolName, setSchoolName] = useState('');
  const [currentLogoUrl, setCurrentLogoUrl] = useState('');
  const [selectedLogoFile, setSelectedLogoFile] = useState(null);
  const [previewLogoUrl, setPreviewLogoUrl] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const fetchConfig = useCallback(async () => {
    setIsLoading(true);
    setError('');
    setSuccessMessage('');
    try {
      const response = await fetch('/api/core/school-configurations/');
      if (!response.ok) {
        throw new Error(`Error HTTP: ${response.status} - ${response.statusText}`);
      }
      const data = await response.json();
      if (data && data.length > 0) {
        const currentConfig = data[0]; // Asumimos que siempre hay una y es la primera
        setConfig(currentConfig);
        setConfigId(currentConfig.id);
        setSchoolName(currentConfig.name || '');
        setCurrentLogoUrl(currentConfig.logo || '');
        setPreviewLogoUrl(currentConfig.logo || ''); // Inicialmente la preview es el logo actual
      } else if (data && !Array.isArray(data)) { // Si la API devuelve un solo objeto
        setConfig(data);
        setConfigId(data.id);
        setSchoolName(data.name || '');
        setCurrentLogoUrl(data.logo || '');
        setPreviewLogoUrl(data.logo || '');
      } else {
        setError('No se encontró la configuración escolar. Contacte al administrador para crear una.');
      }
    } catch (e) {
      console.error('Error al obtener la configuración escolar:', e);
      setError(`Error al obtener la configuración: ${e.message}. Verifique la consola para más detalles.`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  const handleLogoChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedLogoFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewLogoUrl(reader.result);
      };
      reader.readAsDataURL(file);
    } else {
      setSelectedLogoFile(null);
      setPreviewLogoUrl(currentLogoUrl); // Si se deselecciona, volver a la preview del logo actual
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccessMessage('');

    if (!configId) {
      setError("No se puede actualizar la configuración: ID no encontrado.");
      setIsLoading(false);
      return;
    }

    const formData = new FormData();
    formData.append('name', schoolName);
    if (selectedLogoFile) {
      formData.append('logo', selectedLogoFile);
    }
    // Si no se selecciona un nuevo logo, el backend no debería cambiar el existente si 'logo' no está en FormData.
    // Si se quisiera eliminar el logo, se necesitaría una lógica adicional (ej. un checkbox y enviar logo como null o un string vacío especial).

    try {
      const response = await fetch(`/api/core/school-configurations/${configId}/`, {
        method: 'PATCH', // o 'PUT' si reemplaza todo el objeto
        body: formData,
        // No establecer 'Content-Type': 'multipart/form-data', el navegador lo hace automáticamente con FormData
        // Asegúrate de que el backend (Django) esté configurado para manejar CSRF si es necesario (ej. enviando token CSRF)
        // Por ahora, asumimos que la sesión o JWT manejan la autenticación/autorización.
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(`Error HTTP: ${response.status} - ${JSON.stringify(errorData)}`);
      }

      const updatedConfig = await response.json();
      setConfig(updatedConfig);
      setSchoolName(updatedConfig.name || '');
      setCurrentLogoUrl(updatedConfig.logo || '');
      setPreviewLogoUrl(updatedConfig.logo || '');
      setSelectedLogoFile(null); // Limpiar el archivo seleccionado después de subir
      setSuccessMessage('¡Configuración actualizada con éxito!');
      // Opcional: forzar recarga de MainLayout si no se actualiza automáticamente
      // window.dispatchEvent(new CustomEvent('configUpdated'));
    } catch (e) {
      console.error('Error al actualizar la configuración escolar:', e);
      setError(`Error al actualizar: ${e.message}. Revise la consola.`);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading && !config) { // Muestra cargando solo si no hay datos previos
    return <div className="school-config-page"><p>Cargando configuración escolar...</p></div>;
  }

  if (error && !config) { // Muestra error solo si no hay datos previos y falla la carga inicial
     return <div className="school-config-page error-message"><p>{error}</p></div>;
  }

  // Si hay un error pero tenemos config (error durante un update), lo mostramos dentro del form.

  return (
    <div className="school-config-page">
      <h1>Configuración Escolar</h1>
      {isLoading && <p>Actualizando...</p>}
      {error && <p className="error-message">{error}</p>}
      {successMessage && <p className="success-message">{successMessage}</p>}

      {config ? (
        <form onSubmit={handleSubmit} className="config-form">
          <div className="form-group">
            <label htmlFor="schoolName">Nombre del Colegio:</label>
            <input
              type="text"
              id="schoolName"
              value={schoolName}
              onChange={(e) => setSchoolName(e.target.value)}
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="schoolLogo">Logo del Colegio:</label>
            {previewLogoUrl ? (
              <img src={previewLogoUrl} alt="Vista previa del logo" className="logo-preview" />
            ) : (
              <p>No hay logo actualmente.</p>
            )}
            <input
              type="file"
              id="schoolLogo"
              accept="image/*"
              onChange={handleLogoChange}
              disabled={isLoading}
            />
            {selectedLogoFile && <p>Archivo seleccionado: {selectedLogoFile.name}</p>}
          </div>

          {/* Aquí se podrían añadir más campos de SchoolConfiguration si existieran */}

          <button type="submit" disabled={isLoading} className="submit-button">
            {isLoading ? 'Guardando...' : 'Guardar Cambios'}
          </button>
        </form>
      ) : (
        !isLoading && <p>No se pudo cargar la configuración. Si el error persiste, contacte al administrador.</p>
      )}
    </div>
  );
}

export default SchoolConfigurationPage;
