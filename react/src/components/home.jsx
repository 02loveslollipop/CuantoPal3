import React, { useState, useEffect } from 'react';
import { Plus, Trash2 } from 'lucide-react';
import { CurrentSubject } from '../utils/CurrentSubject';
import { Subject } from '../utils/Subject';
import { SettingsManager } from '../utils/settingsManager';
import { Alert } from './alert';

const maxGrades = 100;

export const Home = (
  { 
    onCalculate,
    toSettings
  }
  ) => {
  const [grades, setGrades] = useState([
    { id: 1, percentage: '', grade: '' }
  ]);
  const [showOutofBoundsPercentageAlert, setShowOutofBoundsPercentageAlert] = useState(false);
  const [showOutofBoundsGradeAlert, setShowOutofBoundsGradeAlert] = useState(false);
  const [showNoGradesAlert, setShowNoGradesAlert] = useState(false);

  const settingsManager = SettingsManager.getInstance();

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

  const outOfBoundsGradeAlertMessage = () => {
    return `Las notas deben estar entre ${settingsManager.minValue} y ${settingsManager.maxValue}, si necesitas cambiar los límites, cambialos en la configuración.`;

  }

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
      subject.calculateRequiredGrade();
      const totalPercentage = subject.totalPercentage;

      //TODO: Check if the grades are in range and show an alert if not
      //TODO: Check if the percentage is greater than 100 and show an alert if not

      if(grades.length === 1 && (grades[0].percentage === '' || grades[0].grade === '')){
        setShowNoGradesAlert(true);
        return;
      }
      let gradesCount = 0;
      for (let i = 0; i < grades.length; i++) {
        if (grades[i].percentage !== '' && grades[i].grade !== '') {
          gradesCount++;
        }
        else if (grades[i].percentage === '' ^ grades[i].grade === '') {
          setShowNoGradesAlert(true);
          return;
        }
        else if (gradesCount === 0) {
          setShowNoGradesAlert(true);
          return;
        }
      }

      
      // Check if any grade is out of bounds
      const hasOutOfBoundsGrade = grades.some(grade => 
        grade.grade < settingsManager.minValue || grade.grade > settingsManager.maxValue
      );
      if (hasOutOfBoundsGrade) {
        setShowOutofBoundsGradeAlert(true);
        return;
      }

      // Check if total percentage is greater than 100
      if (totalPercentage > 100) {
        setShowOutofBoundsPercentageAlert(true);
        return;
      }
      onCalculate()
    
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
    <div>
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
          onClick={handleCalculate}
        >
          Calcular
        </button>
      </div>
      <Alert
          isVisible={showOutofBoundsPercentageAlert}
          title={`La suma de los porcentajes es mayor al 100%`}
          message="Por favor verifica los porcentajes de las notas ingresadas, para que la suma sea menor o igual a 100%."
          confirmLabel="Ok"
          showCancel={false}
          onConfirm={() => setShowOutofBoundsPercentageAlert(false)}
        />
      <Alert
          isVisible={showOutofBoundsGradeAlert}
          title={`Una o más notas están fuera de los límites`}
          message={outOfBoundsGradeAlertMessage()}
          confirmLabel="Configurar"
          showCancel={true}
          onCancel={() => setShowOutofBoundsGradeAlert(false)}
          onConfirm={() => {//TODO: Navigate to settings
            setShowOutofBoundsGradeAlert(false);
            toSettings();
          }}
      />
      <Alert
          isVisible={showNoGradesAlert}
          title={`No se puede calcular`}
          message="Alguna de las notas no tiene valor o porcentaje, por favor verifica las notas ingresadas para realizar el cálculo."
          confirmLabel="Ok"
          showCancel={false}
          onConfirm={() => setShowNoGradesAlert(false)}
        />
    </div>
    
  );
};