import React, { useState, useEffect } from 'react';
import { Plus, Trash2 } from 'lucide-react';
import { CurrentSubject } from '../utils/CurrentSubject';
import { Subject } from '../utils/Subject';
import { SettingsManager } from '../utils/settingsManager';
import { Alert } from './alert';

// Número máximo de notas que se pueden agregar.
const maxGrades = 100;


/*Componente Home
Este componente permite al usuario ingresar notas y porcentajes para calcular
cuánto necesita para aprobar un curso. Además, se encarga de sincronizar la información
y mostrar alertas en caso de errores en la entrada de datos.*/

export const Home = (
  { 
    onCalculate,  // Función que se ejecuta para calcular el resultado final.
    toSettings  // Función que redirige a la configuración.
  }
  ) => {
  // Estado para almacenar las notas ingresadas. Cada nota tiene un id, un porcentaje y un valor.
  const [grades, setGrades] = useState([
    { id: 1, percentage: '', grade: '' }
  ]);
  // Controlar la visibilidad de las alertas de error.
  const [showOutofBoundsPercentageAlert, setShowOutofBoundsPercentageAlert] = useState(false);
  const [showOutofBoundsGradeAlert, setShowOutofBoundsGradeAlert] = useState(false);
  const [showNoGradesAlert, setShowNoGradesAlert] = useState(false);

  const settingsManager = SettingsManager.getInstance();

  /*useEffect que se ejecuta al montar el componente.
  Inicializa el CurrentSubject si no existe y carga las notas previamente guardadas.*/

  useEffect(() => {
    // Inicializa CurrentSubject si no existe
    const currentSubject = CurrentSubject.getInstance();
    if (!currentSubject.getCurrentSubject()) {
      currentSubject.setCurrentSubject(new Subject('Current Course'));
    }

    // Carga las notas existentes del CurrentSubject, si hay alguna.
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

  /* Función para agregar una nueva nota al listado.
  Solo permite agregar si el número actual de notas es menor que maxGrades.*/
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

  // Función que genera el mensaje de alerta para cuando una nota está fuera de los límites.
  const outOfBoundsGradeAlertMessage = () => {
    return `Las notas deben estar entre ${settingsManager.minValue} y ${settingsManager.maxValue}, si necesitas cambiar los límites, cambialos en la configuración.`;

  }

  /* Función para manejar los cambios de nota y porcentaje.
  Actualiza el estado local y sincroniza los cambios.*/
  const handleChange = (id, field, value) => {
    const updatedGrades = grades.map(grade => 
      grade.id === id ? {...grade, [field]: value} : grade
    );
    setGrades(updatedGrades);
    updateCurrentSubject(updatedGrades);
  };

  /* Función para remover una nota del listado.
  Actualiza el estado local y sincroniza los cambios.*/
  const handleRemoveGrade = (id) => {
    let updatedGrades;
    // Si solo existe una nota, se reinicia a un estado vacío.
    if (grades.length === 1) {
      updatedGrades = [{ id: 1, percentage: '', grade: '' }];
    } else {  // Se actualiza la numeración de los id de las notas restantes.
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

  /* Función para calcular el resultado final.
  Verifica que las notas ingresadas sean válidas y realiza el cálculo.*/
  const handleCalculate = () => {
    const currentSubject = CurrentSubject.getInstance();
    const subject = currentSubject.getCurrentSubject();
    
    if (subject) {
      subject.calculateFinalGrade();
      subject.calculateRequiredGrade();
      const totalPercentage = subject.totalPercentage;

      //TODO: Check if the grades are in range and show an alert if not
      //TODO: Check if the percentage is greater than 100 and show an alert if not

      // Verifica que si existe solo una nota, ésta no esté vacía.
      if(grades.length === 1 && (grades[0].percentage === '' || grades[0].grade === '')){
        setShowNoGradesAlert(true);
        return;
      }
      let gradesCount = 0;
      // Itera sobre las notas para validar que todas tengan tanto porcentaje como nota.
      for (let i = 0; i < grades.length; i++) {
        if (grades[i].percentage !== '' && grades[i].grade !== '') {
          gradesCount++;
        }
        // Si solo uno de los campos está vacío, muestra la alerta.
        else if (grades[i].percentage === '' ^ grades[i].grade === '') {
          setShowNoGradesAlert(true);
          return;
        }
        // Si no hay notas, muestra la alerta.
        else if (gradesCount === 0) {
          setShowNoGradesAlert(true);
          return;
        }
      }

      
      // Verifica si alguna nota está fuera de los límites establecidos en la configuración.
      const hasOutOfBoundsGrade = grades.some(grade => 
        grade.grade < settingsManager.minValue || grade.grade > settingsManager.maxValue
      );
      if (hasOutOfBoundsGrade) {
        setShowOutofBoundsGradeAlert(true);
        return;
      }

      // Verifica si el porcentaje total supera el 100%.
      if (totalPercentage > 100) {
        setShowOutofBoundsPercentageAlert(true);
        return;
      }
      // Si todas las validaciones son correctas, se procede con el cálculo.
      onCalculate()
    
    }
  }

  // Función para actualizar las notas con el objeto CurrentSubject.
  const updateCurrentSubject = (updatedGrades) => {
    const currentSubject = CurrentSubject.getInstance();
    const subject = currentSubject.getCurrentSubject();
    
    if (subject) {
      // Elimina todas las notas existentes del CurrentSubject.
      while (subject.grades.length > 0) {
        subject.removeGrade(0);
      }

      // Agrega las nuevas notas que tengan valores válidos.
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
              {/* Grupo de input para la nota */}
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
              {/* Grupo de input para el porcentaje */}
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

              {/* Botón para eliminar la nota */}
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

        {/* Botón para agregar una nueva nota */}
        {grades.length < maxGrades && (
          <button 
            className="home__add-button"
            onClick={handleAddGrade}
          >
            <Plus size={24} />
            Agregar nota
          </button>
        )}

        {/* Botón para calcular el resultado final */}
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