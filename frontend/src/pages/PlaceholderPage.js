import React from 'react';

function PlaceholderPage({ title, model }) {
  return (
    <div className="placeholder-page">
      <h1>{title}</h1>
      {model && <p>Contenido para el modelo: <strong>{model}</strong> vendrá aquí.</p>}
      <p>Esta es una página de marcador de posición. La funcionalidad real se implementará pronto.</p>
    </div>
  );
}

export default PlaceholderPage;
