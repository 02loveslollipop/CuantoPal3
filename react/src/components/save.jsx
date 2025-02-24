import React, { useState } from 'react';
import { SubjectsManager } from '../utils/subjectManager';
import { CurrentSubject } from '../utils/CurrentSubject';

export const Save = ({
    setActiveNavIndex
}) => {
    const [subjectName, setSubjectName] = useState('');

    const handleSave = () => {
        if (subjectName.trim() === '') return;

        const subjectManager = SubjectsManager.getInstance();
        subjectManager.saveCurrentSubject(subjectName);
        setActiveNavIndex(0); // Return to home
        
    };

    return (
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
    );
};