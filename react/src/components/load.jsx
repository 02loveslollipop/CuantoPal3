import React from 'react';
import { SubjectsManager } from '../utils/subjectManager';
import { Download } from 'lucide-react';
import { truncateString } from '../utils/Utils';

export const Load = ({
        setActiveNavIndex
    }) => {
    const subjectManager = SubjectsManager.getInstance();
    const subjects = subjectManager.getAllSubjectNames();

    const handleLoad = (subjectName) => {
        console.log(`Loading subject: ${subjectName}`); //TODO: Remove this line
        subjectManager.setCurrentSubject(subjectName);
        // Return to home
        setActiveNavIndex(0);
    };

    return (
        <div className="load__container">
            <div className="load__header">
                <h2 className="load__title">Cargar</h2>
            </div>
            
            <div className="load__group">
                {subjects.map((subjectName) => (
                    <button
                        key={subjectName}
                        className="load__row"
                        onClick={() => handleLoad(subjectName)}
                    >
                        <span className="load__label">{truncateString(subjectName)}</span>
                        <Download size={20} className="load__icon" />
                    </button>
                ))}
                
                {subjects.length === 0 && (
                    <div className="load__empty">
                        <span>No hay materias guardadas</span>
                    </div>
                )}
            </div>
        </div>
    );
};