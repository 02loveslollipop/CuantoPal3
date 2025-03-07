import React from 'react';
import { SubjectsManager } from '../utils/subjectManager';
import { Download, Trash2 } from 'lucide-react';
import { truncateString } from '../utils/Utils';

/* Componente Load
Permite al usuario cargar y eliminar materias previamente guardadas.
Utiliza SubjectsManager para acceder y modificar la lista de materias.*/

export const Load = ({
    setActiveNavIndex   // Función para actualizar el índice de navegación activo.
}) => {
    // Estado usado para forzar la re-renderización del componente cuando se elimina una materia.
    const [refreshKey, setRefreshKey] = React.useState(0);
    // Obtiene la instancia del SubjectsManager para gestionar las materias.
    const subjectManager = SubjectsManager.getInstance();
    // Recupera todos los nombres de las materias guardadas.
    const subjects = subjectManager.getAllSubjectNames();

    // Maneja la carga de una materia.
    // Detiene la propagación del evento para evitar conflictos con otros manejadores de eventos.
    const handleLoad = (subjectName, event) => {
        event.stopPropagation();
        subjectManager.setCurrentSubject(subjectName);
        // Actualiza el índice de navegación para volver a la pantalla principal.
        setActiveNavIndex(0);
    };

    // Maneja la eliminación de una materia.
    const handleDelete = (subjectName, event) => {
        event.stopPropagation();
        subjectManager.deleteSubject(subjectName);
        // Forzar re-renderizado actualizando refreshKey.
        setRefreshKey(prev => prev + 1);
    };

    return (
        <div className="load__container">
            <div className="load__header">
                <h2 className="load__title">Cargar</h2>
            </div>
            
            <div className="load__group">
                {subjects.map((subjectName) => (
                    <div
                        key={subjectName}
                        className="load__row"
                    >
                        <span className="load__label">{truncateString(subjectName)}</span>
                        <div className="load__actions">
                            {/* Botón para cargar la materia */}
                            <button 
                                className="load__load-button"
                                onClick={(e) => handleLoad(subjectName, e)}
                                aria-label="Load subject"
                            >
                                <Download size={20} className="load__icon" />
                            </button>
                            {/* Botón para eliminar la materia */}
                            <button 
                                className="load__remove-button"
                                onClick={(e) => handleDelete(subjectName, e)}
                                aria-label="Remove subject"
                            >
                                <Trash2 size={20} />
                            </button>
                        </div>
                    </div>
                ))}
                
                {/* Muestra un mensaje si no hay materias guardadas */}
                {subjects.length === 0 && (
                    <div className="load__empty">
                        <span>No hay materias guardadas</span>
                    </div>
                )}
            </div>
        </div>
    );
};