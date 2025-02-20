export class SettingsManager {
    private static instance: SettingsManager;
    private _minAcceptValue: number;
    private _minValue: number;
    private _maxValue: number;
  
    private constructor() {
      const savedSettings = localStorage.getItem('settings');
      if (savedSettings) {
        const parsed = JSON.parse(savedSettings);
        this._minAcceptValue = parsed.minAcceptValue;
        this._minValue = parsed.minValue;
        this._maxValue = parsed.maxValue;
      } else {
        this._minAcceptValue = 3;
        this._minValue = 0;
        this._maxValue = 5;
        this.saveToStorage();
      }
    }
  
    public static getInstance(): SettingsManager {
      if (!SettingsManager.instance) {
        SettingsManager.instance = new SettingsManager();
      }
      return SettingsManager.instance;
    }
  
    private saveToStorage(): void {
      localStorage.setItem('settings', JSON.stringify({
        minAcceptValue: this._minAcceptValue,
        minValue: this._minValue,
        maxValue: this._maxValue
      }));
    }
  
    get minAcceptValue(): number {
      return this._minAcceptValue;
    }
  
    set minAcceptValue(value: number) {
      this._minAcceptValue = value;
      this.saveToStorage();
    }
  
    get minValue(): number {
      return this._minValue;
    }
  
    set minValue(value: number) {
      if (value > this._maxValue) {
        value = this._maxValue;
      }
      if (value > this._minAcceptValue) {
        this._minAcceptValue = value;
      }
      this._minValue = value;
      this.saveToStorage();
    }
  
    get maxValue(): number {
      return this._maxValue;
    }
  
    set maxValue(value: number) {
      if (value < this._minAcceptValue) {
        this._minAcceptValue = value;
      }
      this._maxValue = value;
      this.saveToStorage();
    }
  }