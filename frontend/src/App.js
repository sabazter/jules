import React, { useState } from 'react'; // Import useState
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import PlaceholderPage from './pages/PlaceholderPage';
import NivelEducativoPage from './pages/NivelEducativoPage';
import './App.css';

// Importar algunos iconos de ejemplo (Font Awesome)
import { FaCog, FaCalendarAlt, FaBook, FaUsers, FaUserGraduate, FaChalkboardTeacher, FaComments, FaLayerGroup, FaUserShield, FaFileAlt, FaListOl, FaUserCheck, FaUserTag, FaFileInvoice, FaClipboardList, FaFileUpload, FaTasks, FaGraduationCap, FaSchool, FaRegListAlt, FaUserTie } from 'react-icons/fa';
import { MdAccessTime, MdGrade, MdOutlinePolicy, MdOutlinePriceChange, MdAssignmentInd } from "react-icons/md"; // Cambiado MdOutlinePeriod a MdAccessTime


function App() {
  // El estado ahora controla si el *mouse está sobre la sidebar* o no.
  // Inicialmente, consideramos que no está expandida (mouse no encima).
  const [isSidebarHovered, setIsSidebarHovered] = useState(false);

  // Estas funciones serán llamadas por onMouseEnter y onMouseLeave en Sidebar.js
  const handleSidebarMouseEnter = () => {
    setIsSidebarHovered(true);
  };

  const handleSidebarMouseLeave = () => {
    setIsSidebarHovered(false);
  };

  // Definimos los grupos y elementos de la sidebar con iconos
  const sidebarGroups = [
    {
      name: "Gestión Académica Principal",
      items: [
        { name: "Configuración Escolar", path: "/configuracion-escolar", model: "core.SchoolConfiguration", icon: <FaSchool /> },
        { name: "Año Académico", path: "/ano-academico", model: "core.AcademicYear", icon: <FaCalendarAlt /> },
        { name: "Período/Lapso Académico", path: "/periodo-academico", model: "core.AcademicPeriod", icon: <MdAccessTime /> }, // Corregido
        { name: "Nivel Educativo", path: "/nivel-educativo", model: "core.Level", icon: <FaLayerGroup /> },
        { name: "Grado/Año", path: "/grado-ano", model: "core.GradeLevel", icon: <FaGraduationCap /> },
        { name: "Sección", path: "/seccion", model: "core.Section", icon: <FaTasks /> },
        { name: "Asignatura/Materia", path: "/asignatura", model: "core.Subject", icon: <FaBook /> },
        { name: "Escala de Calificación", path: "/escala-calificacion", model: "core.GradingScale", icon: <MdGrade /> },
        { name: "Valor de Calificación", path: "/valor-calificacion", model: "core.GradeValue", icon: <MdOutlinePriceChange /> },
        { name: "Asignación de Materia a Grado", path: "/asignacion-materia-grado", model: "core.SubjectAssignment", icon: <MdAssignmentInd /> },
      ]
    },
    {
      name: "Usuarios y Roles",
      items: [
        { name: "Usuarios", path: "/usuarios", model: "core.User", icon: <FaUsers /> },
        { name: "Grupos de Permisos", path: "/grupos-permisos", model: "auth.Group", icon: <FaUserShield /> },
      ]
    },
    {
      name: "Estudiantes",
      items: [
        { name: "Planillas de Preinscripción", path: "/planillas-preinscripcion", model: "core.PreEnrollmentProfile", icon: <FaFileAlt /> },
        { name: "Inscripciones de Estudiantes", path: "/inscripciones-estudiantes", model: "core.StudentEnrollment", icon: <FaUserCheck /> },
        { name: "Boletas de Calificaciones", path: "/boletas-calificaciones", model: "core.ReportCard", icon: <FaFileInvoice /> },
        { name: "Calificaciones Finales (Lapso)", path: "/calificaciones-finales-lapso", model: "core.StudentGrade", icon: <FaListOl /> },
        { name: "Entregas de Estudiantes", path: "/entregas-estudiantes", model: "students.StudentSubmission", icon: <FaFileUpload /> },
      ]
    },
    {
      name: "Profesores y Personal",
      items: [
        { name: "Asignación de Coordinador", path: "/asignacion-coordinador", model: "core.CoordinatorAssignment", icon: <FaUserTie /> },
        { name: "Asignación de Profesor Guía", path: "/asignacion-profesor-guia", model: "core.GuideTeacherAssignment", icon: <FaUserTag /> },
        { name: "Asignación de Profesor a Materia/Sección", path: "/asignacion-profesor-materia", model: "core.TeacherSubjectSectionAssignment", icon: <FaChalkboardTeacher /> },
        { name: "Actividades Evaluativas", path: "/actividades-evaluativas", model: "teachers.Activity", icon: <FaRegListAlt /> },
        { name: "Actividades del Plan de Evaluación", path: "/actividades-plan-evaluacion", model: "teachers.EvaluationActivity", icon: <FaClipboardList /> },
        { name: "Documentos de Plan de Evaluación", path: "/documentos-plan-evaluacion", model: "teachers.EvaluationPlanDocument", icon: <FaFileAlt /> },
        { name: "Calificaciones de Actividades", path: "/calificaciones-actividades", model: "teachers.Grade", icon: <MdGrade /> },
      ]
    },
    {
      name: "Comunicación",
      items: [
        { name: "Mensajes de Chat", path: "/mensajes-chat", model: "core.ChatMessage", icon: <FaComments /> },
        { name: "Salas de Chat", path: "/salas-chat", model: "core.ChatRoom", icon: <FaComments /> },
      ]
    }
  ];

  return (
    <Router>
      {/* La clase para ajustar el main-content ahora depende de isSidebarHovered */}
      <div className={`app-container ${isSidebarHovered ? 'sidebar-expanded' : 'sidebar-collapsed'}`}>
        <Sidebar
          groups={sidebarGroups}
          isExpanded={isSidebarHovered} // Pasamos isSidebarHovered como isExpanded
          // No pasamos toggleSidebar, sino las funciones de mouse enter/leave
          onMouseEnter={handleSidebarMouseEnter}
          onMouseLeave={handleSidebarMouseLeave}
        />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<PlaceholderPage title="Página de Inicio" />} />
            {/* Mapeo dinámico de rutas para PlaceholderPage, excepto para las que tienen componente específico */}
            {sidebarGroups.flatMap(group =>
              group.items
                .filter(item => item.path !== "/nivel-educativo") // Excluir la ruta que ahora tiene componente
                .map(item => (
                  <Route
                    key={item.path}
                    path={item.path}
                    element={<PlaceholderPage title={item.name} model={item.model} />}
                  />
                ))
            )}
            {/* Ruta específica para Nivel Educativo */}
            <Route path="/nivel-educativo" element={<NivelEducativoPage />} />

            {/* Ruta por defecto si ninguna coincide */}
            <Route path="*" element={<PlaceholderPage title="Página no encontrada" />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
