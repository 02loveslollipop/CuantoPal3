import React, { useState } from 'react';
import { SubjectsManager } from '../utils/subjectManager';
import { CurrentSubject } from '../utils/CurrentSubject';
import { Alert } from './alert';

export const Save = ({
    setActiveNavIndex
}) => {
    const [subjectName, setSubjectName] = useState('');
    const [showSubjectExistsAlert, setShowSubjectExistsAlert] = useState(false);
    const [showNoNameAlert, setShowNoNameAlert] = useState(false);
    const [showEmptySubjectAlert, setShowEmptySubjectAlert] = useState(false);

    const handleSave = () => {
        if (subjectName.trim() === '') {
            setShowNoNameAlert(true);
            return;
        }
        if (CurrentSubject.getInstance().getCurrentSubject().isEmpty()) {
            setShowEmptySubjectAlert(true);
            return;
        }
        const subjectManager = SubjectsManager.getInstance();
        //Check if subject already exists in SubjectsManager
        if (subjectManager.subjetExists(subjectName)) {
            setShowSubjectExistsAlert(true);
            return;

        }
        handleSaveOverwrite();
        
    };

    const handleSaveOverwrite = () => {
        const subjectManager = SubjectsManager.getInstance();
        subjectManager.saveCurrentSubject(subjectName);
        setActiveNavIndex(0); // Return to home
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

                <button 
                    className="save__button"
                    onClick={handleSave}
                >
                    Guardar
                </button>
            </div>
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