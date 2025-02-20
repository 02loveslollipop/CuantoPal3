import React, { useState } from 'react';
import { Plus, Trash2 } from 'lucide-react';

const maxGrades = 100;

export const Home = () => {
  const [grades, setGrades] = useState([
    { id: 1, percentage: '', grade: '' }
  ]);

  const handleAddGrade = () => {
    if (grades.length < maxGrades) {
      const newGrade = {
        id: grades.length + 1,
        percentage: '',
        grade: ''
      };
      setGrades([...grades, newGrade]);
    }
  };

  const handleChange = (id, field, value) => {
    setGrades(grades.map(grade => 
      grade.id === id ? {...grade, [field]: value} : grade
    ));
  };

  const handleRemoveGrade = (id) => {
    if (grades.length === 1) {
      // If it's the last grade, reset it to empty
      setGrades([{ id: 1, percentage: '', grade: '' }]);
    } else {
      // Remove the grade and reindex remaining grades
      const filteredGrades = grades
        .filter(grade => grade.id !== id)
        .map((grade, index) => ({
          ...grade,
          id: index + 1
        }));
      setGrades(filteredGrades);
    }
  };

  return (
    <div className="home__container">
      <div className="home__header">
        <h2 className="home__title">
          Conoce cuanto necesitas para aprobar tu curso!
        </h2>
      </div>

      <div className="home__grades-container">
        {grades.map((grade) => (
          <div key={grade.id} className="home__grade-row">
            <div className="home__input-group">
              <label>Porcentaje</label>
              <input 
                type="number"
                min="0"
                max="100"
                value={grade.percentage}
                onChange={(e) => handleChange(grade.id, 'percentage', e.target.value)}
                className="home__input"
                placeholder="0"
              />
              <span className="home__percentage">%</span>
            </div>

            <div className="home__input-group">
              <label>Nota</label>
              <input
                type="number"
                min="0"
                max="7"
                step="0.1"
                value={grade.grade}
                onChange={(e) => handleChange(grade.id, 'grade', e.target.value)}
                className="home__input"
                placeholder="0.0"
              />
            </div>

            <button 
              className="home__remove-button"
              onClick={() => handleRemoveGrade(grade.id)}
              aria-label="Remove grade"
            >
              <Trash2 size={20} />
            </button>
          </div>
        ))}
      </div>

      {grades.length < maxGrades && (
        <button 
          className="home__add-button"
          onClick={handleAddGrade}
        >
          <Plus size={24} />
          Agregar nota
        </button>
      )}

      <button className="home__calculate-button">
        Calcular
      </button>
    </div>
  );
};