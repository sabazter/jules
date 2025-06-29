import React from 'react';
import { NavLink } from 'react-router-dom'; // Usar NavLink para activeClassName
import './Sidebar.css';
// Ya no necesitamos FaBars, FaTimes para el botón

function Sidebar({ groups, isExpanded, onMouseEnter, onMouseLeave }) {
  return (
    <aside
      className={`sidebar ${isExpanded ? 'expanded' : 'collapsed'}`}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      <div className="sidebar-header">
        {/* El título solo se muestra si está expandido, no hay botón de toggle */}
        {isExpanded && <h3>Navegación</h3>}
      </div>
      <nav className="sidebar-nav">
        {groups.map((group, index) => (
          <div key={index} className="sidebar-group">
            {isExpanded ? (
              <h4>{group.name}</h4>
            ) : (
              <hr className="sidebar-group-separator" /> // Separador simple cuando está colapsada
            )}
            <ul>
              {group.items.map((item) => (
                <li key={item.path} title={isExpanded ? '' : item.name}> {/* Tooltip para modo colapsado */}
                  <NavLink
                    to={item.path}
                    className={({ isActive }) => isActive ? "sidebar-link active" : "sidebar-link"}
                  >
                    {item.icon && <span className="sidebar-icon">{item.icon}</span>}
                    {isExpanded && <span className="sidebar-link-text">{item.name}</span>}
                  </NavLink>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>
    </aside>
  );
}

export default Sidebar;
