import { Subject, IGrade } from "./Subject";

export class CurrentSubject {
    private static instance: CurrentSubject;
    private _currentSubject: Subject | null;

    private constructor() {
        this._currentSubject = new Subject("");
    }

    public static getInstance(): CurrentSubject {
        if (!CurrentSubject.instance) {
            CurrentSubject.instance = new CurrentSubject();
        }
        return CurrentSubject.instance;
    }

    public setCurrentSubject(subject: Subject): void {
        this._currentSubject = subject;
    }

    public getCurrentSubject(): Subject | null {
        return this._currentSubject;
    }
}
