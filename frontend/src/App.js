import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import PlaceholderPage from './pages/PlaceholderPage';
import NivelEducativoPage from './pages/NivelEducativoPage'; // Importar la nueva página
import './App.css';

function App() {
  // Definimos los grupos y elementos de la sidebar para pasarlos como props
  // Esta estructura la obtuvimos de tu solicitud inicial
  const sidebarGroups = [
    {
      name: "Gestión Académica Principal",
      items: [
        { name: "Configuración Escolar", path: "/configuracion-escolar", model: "core.SchoolConfiguration" },
        { name: "Año Académico", path: "/ano-academico", model: "core.AcademicYear" },
        { name: "Período/Lapso Académico", path: "/periodo-academico", model: "core.AcademicPeriod" },
        { name: "Nivel Educativo", path: "/nivel-educativo", model: "core.Level" },
        { name: "Grado/Año", path: "/grado-ano", model: "core.GradeLevel" },
        { name: "Sección", path: "/seccion", model: "core.Section" },
        { name: "Asignatura/Materia", path: "/asignatura", model: "core.Subject" },
        { name: "Escala de Calificación", path: "/escala-calificacion", model: "core.GradingScale" },
        { name: "Valor de Calificación", path: "/valor-calificacion", model: "core.GradeValue" },
        { name: "Asignación de Materia a Grado", path: "/asignacion-materia-grado", model: "core.SubjectAssignment" },
      ]
    },
    {
      name: "Usuarios y Roles",
      items: [
        { name: "Usuarios", path: "/usuarios", model: "core.User" },
        { name: "Grupos de Permisos", path: "/grupos-permisos", model: "auth.Group" },
      ]
    },
    {
      name: "Estudiantes",
      items: [
        { name: "Planillas de Preinscripción", path: "/planillas-preinscripcion", model: "core.PreEnrollmentProfile" },
        { name: "Inscripciones de Estudiantes", path: "/inscripciones-estudiantes", model: "core.StudentEnrollment" },
        { name: "Boletas de Calificaciones", path: "/boletas-calificaciones", model: "core.ReportCard" },
        { name: "Calificaciones Finales (Lapso)", path: "/calificaciones-finales-lapso", model: "core.StudentGrade" },
        { name: "Entregas de Estudiantes", path: "/entregas-estudiantes", model: "students.StudentSubmission" },
      ]
    },
    {
      name: "Profesores y Personal",
      items: [
        { name: "Asignación de Coordinador", path: "/asignacion-coordinador", model: "core.CoordinatorAssignment" },
        { name: "Asignación de Profesor Guía", path: "/asignacion-profesor-guia", model: "core.GuideTeacherAssignment" },
        { name: "Asignación de Profesor a Materia/Sección", path: "/asignacion-profesor-materia", model: "core.TeacherSubjectSectionAssignment" },
        { name: "Actividades Evaluativas", path: "/actividades-evaluativas", model: "teachers.Activity" },
        { name: "Actividades del Plan de Evaluación", path: "/actividades-plan-evaluacion", model: "teachers.EvaluationActivity" },
        { name: "Documentos de Plan de Evaluación", path: "/documentos-plan-evaluacion", model: "teachers.EvaluationPlanDocument" },
        { name: "Calificaciones de Actividades", path: "/calificaciones-actividades", model: "teachers.Grade" },
      ]
    },
    {
      name: "Comunicación",
      items: [
        { name: "Mensajes de Chat", path: "/mensajes-chat", model: "core.ChatMessage" },
        { name: "Salas de Chat", path: "/salas-chat", model: "core.ChatRoom" },
      ]
    }
  ];

  return (
    <Router>
      <div className="app-container">
        <Sidebar groups={sidebarGroups} />
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
