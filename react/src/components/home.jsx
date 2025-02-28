import React, { useState, useEffect } from 'react';
import { Plus, Trash2 } from 'lucide-react';
import { CurrentSubject } from '../utils/CurrentSubject';
import { Subject } from '../utils/Subject';

const maxGrades = 100;

export const Home = () => {
  const [grades, setGrades] = useState([
    { id: 1, percentage: '', grade: '' }
  ]);

  useEffect(() => {
    // Initialize CurrentSubject if not exists
    const currentSubject = CurrentSubject.getInstance();
    if (!currentSubject.getCurrentSubject()) {
      currentSubject.setCurrentSubject(new Subject('Current Course'));
    }

    // Load existing grades from CurrentSubject
    const subject = currentSubject.getCurrentSubject();
    if (subject && subject.grades.length > 0) {
      const loadedGrades = subject.grades.map((grade, index) => ({
        id: index + 1,
        percentage: grade.percentage,
        grade: grade.value
      }));
      setGrades(loadedGrades);
    }
  }, []);

  const handleAddGrade = () => {
    if (grades.length < maxGrades) {
      const newGrade = {
        id: grades.length + 1,
        percentage: '',
        grade: ''
      };
      setGrades([...grades, newGrade]);
      updateCurrentSubject([...grades, newGrade]);
    }
  };

  const handleChange = (id, field, value) => {
    const updatedGrades = grades.map(grade => 
      grade.id === id ? {...grade, [field]: value} : grade
    );
    setGrades(updatedGrades);
    updateCurrentSubject(updatedGrades);
  };

  const handleRemoveGrade = (id) => {
    let updatedGrades;
    if (grades.length === 1) {
      updatedGrades = [{ id: 1, percentage: '', grade: '' }];
    } else {
      updatedGrades = grades
        .filter(grade => grade.id !== id)
        .map((grade, index) => ({
          ...grade,
          id: index + 1
        }));
    }
    setGrades(updatedGrades);
    updateCurrentSubject(updatedGrades);
  };

  const handleCalculate = () => {
    const currentSubject = CurrentSubject.getInstance();
    const subject = currentSubject.getCurrentSubject();
    
    if (subject) {
      subject.calculateFinalGrade();
      const totalPercentage = subject.totalPercentage();
      const currentGrades = subject.grades;
      const requiredPercentage = subject.remainingPercentage();
      const requiredGrade = subject.calculateRequiredGrade();

      //TODO: push to result page
      console.log('Total Percentage:', totalPercentage);
      console.log('Current Grades:', currentGrades);
      console.log('Required Percentage:', requiredPercentage);
      console.log('Required Grade:', requiredGrade);
    
    }
  }

  const updateCurrentSubject = (updatedGrades) => {
    const currentSubject = CurrentSubject.getInstance();
    const subject = currentSubject.getCurrentSubject();
    
    if (subject) {
      // Clear existing grades
      while (subject.grades.length > 0) {
        subject.removeGrade(0);
      }

      // Add new grades
      updatedGrades.forEach(grade => {
        if (grade.percentage !== '' && grade.grade !== '') {
          subject.addGrade({
            percentage: Number(grade.percentage),
            value: Number(grade.grade)
          });
        }
      });
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

      <button 
        className="home__calculate-button"
        onClick="handleCalculate"
      >
        Calcular
      </button>
    </div>
  );
};