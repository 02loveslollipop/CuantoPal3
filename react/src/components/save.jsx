import React, { useState } from 'react';
import { SubjectsManager } from '../utils/subjectManager';
import { CurrentSubject } from '../utils/CurrentSubject';
import { Alert } from './alert';

/* Componente Save
Permite guardar el curso actual en SubjectsManager, asignándole un nombre.
Valida que el nombre no esté vacío, que el curso tenga notas y que no se duplique.*/

export const Save = ({
    setActiveNavIndex
}) => {
    // Estado para almacenar el nombre del curso a guardar.
    const [subjectName, setSubjectName] = useState('');
    // Estados para controlar la visibilidad de alertas de error.
    const [showSubjectExistsAlert, setShowSubjectExistsAlert] = useState(false);
    const [showNoNameAlert, setShowNoNameAlert] = useState(false);
    const [showEmptySubjectAlert, setShowEmptySubjectAlert] = useState(false);

    // Maneja la acción de guardar el curso.
    const handleSave = () => {
        // Verifica si el nombre del curso está vacío.
        if (subjectName.trim() === '') {
            setShowNoNameAlert(true);
            return;
        }
        // Verifica si el curso actual no tiene notas.
        if (CurrentSubject.getInstance().getCurrentSubject().isEmpty()) {
            setShowEmptySubjectAlert(true);
            return;
        }
        const subjectManager = SubjectsManager.getInstance();
        // Verifica si la materia ya existe en SubjectsManager.
        if (subjectManager.subjetExists(subjectName)) {
            setShowSubjectExistsAlert(true);
            return;

        }
        // Guarda; sobrescribe si es necesario.
        handleSaveOverwrite();
        
    };

    // Función para guardar el curso actual.
    const handleSaveOverwrite = () => {
        const subjectManager = SubjectsManager.getInstance();
        subjectManager.saveCurrentSubject(subjectName);
        setActiveNavIndex(0); // Regresar al menú principal.
    }



    return (
        <div>
            <div className="save__container">
                <div className="save__header">
                    <h2 className="save__title">Guardar</h2>
                </div>
                
                <div className="save__input-container">
                    <div className="save__row">
                        <div className="save__input-group">
                            <label>Nombre del curso</label>
                            <input
                                type="text"
                                value={subjectName}
                                onChange={(e) => setSubjectName(e.target.value)}
                                className="save__input"
                                placeholder="Nombre del curso"
                            />
                        </div>
                    </div>
                </div>

                {/* Botón para iniciar el proceso de guardado */}
                <button 
                    className="save__button"
                    onClick={handleSave}
                >
                    Guardar
                </button>
            </div>
            {/* Alerta para cuando el curso ya existe */}
            <Alert
                    isVisible={showSubjectExistsAlert}
                    title={`${subjectName} ya existe`}
                    message="Este curso ya existe, si guardas el curso con el mismo nombre se sobrescribirán los datos."
                    confirmLabel="Sobreescribir"
                    showCancel={true}
                    isDestructive={true}
                    onConfirm={handleSaveOverwrite}
                    onCancel={() => setShowSubjectExistsAlert(false)}
                />
            {/* Alerta para cuando el curso actual no tiene notas para guardar */}
            <Alert
                    isVisible={showNoNameAlert}
                    title="No se puede guardar"
                    message="El nombre del curso no puede estar vacío."
                    confirmLabel="Aceptar"
                    onConfirm={() => setShowNoNameAlert(false)}
                    showCancel={false}
                />
            <Alert
                    isVisible={showEmptySubjectAlert}
                    title="No se puede guardar"
                    message="El curso no tiene notas para guardar."
                    confirmLabel="Aceptar"
                    onConfirm={() => setShowEmptySubjectAlert(false)}
                    showCancel={false}
                />
        </div>
        
    );
};