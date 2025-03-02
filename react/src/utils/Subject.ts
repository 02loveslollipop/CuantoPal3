import { SettingsManager } from './settingsManager';

export interface IGrade {
    value: number;
    percentage: number;
}

export class Subject {
    private _name: string;
    private _grades: IGrade[];
    private _finalGrade: number | null;
    private _settingsManager: SettingsManager;

    constructor(name: string) {
        this._name = name;
        this._grades = [];
        this._finalGrade = null;
        this._settingsManager = SettingsManager.getInstance();
    }

    public calculateRequiredGrade(): number | null {
        if (this._grades.length === 0 || this.remainingPercentage <= 0) {
            return null;
        }

        const currentWeightedSum = this._grades.reduce(
            (sum, grade) => sum + (grade.value * grade.percentage),
            0
        );

        const minAcceptValue = this._settingsManager.minAcceptValue;
        const minValue = this._settingsManager.minValue;
        const maxValue = this._settingsManager.maxValue;

        // Calculate required grade for remaining percentage
        const requiredGrade = (minAcceptValue * 100 - currentWeightedSum) / this.remainingPercentage;

        return Number(requiredGrade.toFixed(1));
    }

    public addGrade(grade: IGrade): void {
        this._grades.push(grade);
        this.calculateFinalGrade();
    }

    public updateGrade(index: number, grade: IGrade): void {
        if (index >= 0 && index < this._grades.length) {
            this._grades[index] = grade;
            this.calculateFinalGrade();
        }
    }

    public removeGrade(index: number): void {
        if (index >= 0 && index < this._grades.length) {
            this._grades.splice(index, 1);
            this.calculateFinalGrade();
        }
    }

    private calculateFinalGrade(): void {
        if (this._grades.length === 0) {
            this._finalGrade = null;
            return;
        }

        let totalPercentage = 0;
        let weightedSum = 0;

        this._grades.forEach(grade => {
            totalPercentage += grade.percentage;
            weightedSum += (grade.value * grade.percentage);
        });

        this._finalGrade = totalPercentage > 0 ? 
            Number((weightedSum / 100).toFixed(1)) : 
            null;
    }

    public toJSON(): object {
        return {
            name: this._name,
            grades: this._grades,
            finalGrade: this._finalGrade
        };
    }

    public isEmpty(): boolean {
        return this._grades.length === 0;
    }

    public copy(): Subject {
        const copy = new Subject(this._name);
        copy._grades = [...this._grades];
        copy._finalGrade = this._finalGrade;
        return copy;
    }

    // Getters
    get name(): string {
        return this._name;
    }

    get grades(): IGrade[] {
        return [...this._grades];
    }

    get finalGrade(): number | null {
        return this._finalGrade;
    }

    get totalPercentage(): number {
        return this._grades.reduce((sum, grade) => sum + grade.percentage, 0);
    }

    get remainingPercentage(): number {
        return 100 - this.totalPercentage;
    }

    get requiredGrade(): number | null {
        return this.calculateRequiredGrade();
    }
}