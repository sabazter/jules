import React from 'react';
import { Link } from 'react-router-dom';
import './Sidebar.css'; // Crearemos este archivo CSS más tarde

function Sidebar({ groups }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h3>Navegación</h3>
      </div>
      <nav className="sidebar-nav">
        {groups.map((group, index) => (
          <div key={index} className="sidebar-group">
            <h4>{group.name}</h4>
            <ul>
              {group.items.map((item) => (
                <li key={item.path}>
                  <Link to={item.path}>{item.name}</Link>
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
