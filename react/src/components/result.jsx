import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

export const ResultadoGanar = ({ scoreNeeded, remainingPercentage, currentAverage, currentPercentage }) => {
  const navigate = useNavigate();

  const handleBack = () => {
    navigate(-1);
  };

  return (
    <div className="resultado-ganar">
      <div className="nav-bar">
        <div className="back-section" onClick={handleBack}>
          <ArrowLeft className="back-icon" />
          <span className="back-text">Back</span>
        </div>
        <div className="title">Resultado</div>
      </div>
      
      <div className="content">
        <div className="result-card">
          <h1 className="congratulations">Felicitaciones!</h1>
          <p className="needed-score">
            Necesitas {scoreNeeded} en el {remainingPercentage}% para ganar tu materia.
          </p>
          <p className="current-average">
            Actualmente tienes un promedio de {currentAverage} en el {currentPercentage}%
          </p>
        </div>
      </div>
    </div>
  );
};