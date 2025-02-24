import React from 'react';
import { SubjectsManager } from '../utils/subjectManager';
import { Download, Trash2 } from 'lucide-react';
import { truncateString } from '../utils/Utils';

export const Load = ({
    setActiveNavIndex
}) => {
    const subjectManager = SubjectsManager.getInstance();
    const subjects = subjectManager.getAllSubjectNames();

    const handleLoad = (subjectName, event) => {
        event.stopPropagation();
        subjectManager.setCurrentSubject(subjectName);
        setActiveNavIndex(0);
    };

    const handleDelete = (subjectName, event) => {
        event.stopPropagation();
        subjectManager.deleteSubject(subjectName);
        // Force re-render
        setActiveNavIndex(3);
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
                            <button 
                                className="load__load-button"
                                onClick={(e) => handleLoad(subjectName, e)}
                                aria-label="Load subject"
                            >
                                <Download size={20} className="load__icon" />
                            </button>
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
                
                {subjects.length === 0 && (
                    <div className="load__empty">
                        <span>No hay materias guardadas</span>
                    </div>
                )}
            </div>
        </div>
    );
};