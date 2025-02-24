import { Subject, IGrade } from './Subject';
import { CurrentSubject } from './CurrentSubject';

export class SubjectsManager {
    private static instance: SubjectsManager;
    private _subjects: Map<string, Subject>;
    private _currentSubject: CurrentSubject;

    private constructor() {
        this._subjects = new Map();
        this._currentSubject = CurrentSubject.getInstance();
        this.loadFromStorage();
    }

    private loadFromStorage(): void {
        const savedSubjects = localStorage.getItem('subjects');
        if (savedSubjects) {
            const parsed = JSON.parse(savedSubjects);
            Object.entries(parsed).forEach(([name, data]: [string, any]) => {
                const subject = new Subject(name);
                data.grades.forEach((grade: IGrade) => {
                    subject.addGrade(grade);
                });
                this._subjects.set(name, subject);
            });
        }
    }

    private saveToStorage(): void {
        const subjectsObject = Object.fromEntries(
            Array.from(this._subjects.entries()).map(([name, subject]) => [
                name,
                subject.toJSON()
            ])
        );
        localStorage.setItem('subjects', JSON.stringify(subjectsObject));
    }

    public static getInstance(): SubjectsManager {
        if (!SubjectsManager.instance) {
            SubjectsManager.instance = new SubjectsManager();
        }
        return SubjectsManager.instance;
    }

    public createSubject(name: string): Subject {
        const subject = new Subject(name);
        this._subjects.set(name, subject);
        this._currentSubject.setCurrentSubject(subject);
        this.saveToStorage();
        return subject;
    }

    public setCurrentSubject(name: string): Subject | null {
        const subject = this._subjects.get(name);
        if (subject) {
            this._currentSubject.setCurrentSubject(subject);
        }
        return subject || null;
    }

    public getCurrentSubject(): Subject | null {
        return this._currentSubject.getCurrentSubject();
    }

    public getAllSubjectNames(): string[] {
        return Array.from(this._subjects.keys());
    }

    public getSubject(name: string): Subject | null {
        return this._subjects.get(name) || null;
    }

    public deleteSubject(name: string): void {
        if (this._subjects.has(name)) {
            this._subjects.delete(name);
            if (this._currentSubject.getCurrentSubject()?.name === name) {
                this._currentSubject.setCurrentSubject(new Subject(''));
            }
            this.saveToStorage();
        }
    }

    public saveCurrentSubject(name: string): void {
        const currentSubject = this._currentSubject.getCurrentSubject();
        if (currentSubject) {
            const newSubject = new Subject(name);
            currentSubject.grades.forEach(grade => {
                newSubject.addGrade(grade);
            });
            this._subjects.set(name, newSubject);
            this.saveToStorage();
        }
    }
}