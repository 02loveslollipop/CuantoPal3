import React from 'react';
import { SettingsManager } from '../utils/settingsManager';
import { CurrentSubject } from '../utils/CurrentSubject';

/* Componente Result
Muestra el resultado del cálculo del curso actual*/

export const Result = () => {
  // Se obtiene la instancia actual del curso.
  const currentSubject = CurrentSubject.getInstance();
  const subject = currentSubject.getCurrentSubject();
  
  const totalPercentage = subject.totalPercentage;
  const finalGrade = subject.finalGrade;
  const remainingPercentage = subject.remainingPercentage;
  const requiredGrade = subject.requiredGrade;

  // Se obtiene la configuración para conocer el valor mínimo aceptable.
  const settingsManager = SettingsManager.getInstance();
  const minAcceptValue = settingsManager.minAcceptValue;

  /* Función que determina qué contenido mostrar basado en la comparación de la nota requerida
  con el valor mínimo.*/
  const renderContent = () => {
    
    // Si el porcentaje total es 100, se muestra un mensaje indicando que ya tiene el 100% de la materia.
    if (totalPercentage === 100){
      console.log("holi")
      var needed = "Ya tiene el 100% de la materia"
      var condition = finalGrade < minAcceptValue
      var title = condition ? "💀" : "Felicitaciones!"
    } else {
      var needed =`Necesitas ${requiredGrade} en el ${remainingPercentage}% para ganar tu materia.`
      var condition = requiredGrade > minAcceptValue
      var title = condition ? "Cuidado!" : "Felicitaciones!"
    }
    

    // Si la nota requerida es mayor al valor mínimo necesario, se muestra un mensaje de advertencia.
    if (condition) {
      return (
        <div className="result__container__red">
            <div className="result__content">
            <div className="result__card">
                <h1 className="result__card-title">{title}</h1>
                <p className="result__card-needed">
                {needed}
                </p>
                <p className="result__card-current">
                Actualmente tienes un promedio de {finalGrade} en el {totalPercentage}% de la materia.
                </p>
            </div>
            </div>
        </div>
      );
    } else {
      // Si la nota requerida es menor o igual al valor mínimo necesario, se muestra un mensaje de felicitación.
      return (
        <div className="result__container__green">  
            <div className="result__content">
            <div className="result__card">
                <h1 className="result__card-title">{title}</h1>
                <p className="result__card-needed">
                {needed}
                </p>
                <p className="result__card-current">
                Actualmente tienes un promedio de {finalGrade} en el {totalPercentage}% de la materia.
                </p>
            </div>
            </div>
        </div>
      );
    }
  }

  return (
    <div className="result">
        {renderContent()}
    </div>
  );
};