import React from 'react';
import { SettingsManager } from '../utils/settingsManager';
import { CurrentSubject } from '../utils/CurrentSubject';

export const Result = () => {
  const currentSubject = CurrentSubject.getInstance();
  const subject = currentSubject.getCurrentSubject();
  
  const totalPercentage = subject.totalPercentage;
  const finalGrade = subject.finalGrade;
  const remainingPercentage = subject.remainingPercentage;
  const requiredGrade = subject.requiredGrade;
  console.log("hola")

  const settingsManager = SettingsManager.getInstance();
  const minAcceptValue = settingsManager.minAcceptValue;

  const renderContent = () => {
    if (requiredGrade > minAcceptValue) {
      return (
        <div className="result__container__red">
            <div className="result__content">
            <div className="result__card">
                <h1 className="result__card-title">Cuidado!</h1>
                <p className="result__card-needed">
                Necesitas {requiredGrade} en el {remainingPercentage}% para ganar tu materia.
                </p>
                <p className="result__card-current">
                Actualmente tienes un promedio de {finalGrade} en el {totalPercentage}% de la materia.
                </p>
            </div>
            </div>
        </div>
      );
    } else {
      return (
        <div className="result__container__green">  
            <div className="result__content">
            <div className="result__card">
                <h1 className="result__card-title">Felicitaciones!</h1>
                <p className="result__card-needed">
                Necesitas {requiredGrade} en el {remainingPercentage}% para ganar tu materia.
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