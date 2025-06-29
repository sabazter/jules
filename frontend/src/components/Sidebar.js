import React from 'react';
import { Link, NavLink } from 'react-router-dom'; // Usar NavLink para activeClassName
import './Sidebar.css';
import { FaBars, FaTimes } from 'react-icons/fa'; // Iconos para el botón de toggle

function Sidebar({ groups, isExpanded, toggleSidebar }) {
  return (
    <aside className={`sidebar ${isExpanded ? 'expanded' : 'collapsed'}`}>
      <div className="sidebar-header">
        {isExpanded && <h3>Navegación</h3>}
        <button onClick={toggleSidebar} className="sidebar-toggle-btn">
          {isExpanded ? <FaTimes /> : <FaBars />}
        </button>
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
