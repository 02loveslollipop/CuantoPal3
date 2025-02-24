//define an export function that given an string returns it, if the count of characters it's higher than 24, then it will return the first n characters followed by '...' and then the last word of the string such that n + 3 + lastWord.length = 24
export function truncateString(str: string): string {
    const maxLength = 22;
    if (str.length <= maxLength) {
        return str;
    }
    const lastWord = str.split(' ').pop();
    if (!lastWord) {
        return str.slice(0, maxLength - 3) + ' ... ';
    }
    const n = maxLength - 3 - lastWord.length;
    return `${str.slice(0, n)}...${lastWord}`;
}

export function fillLocalStorage(): void {
    const subjectsData = {
        "Calculo diferencial": {
            "grades": [
                { "value": 4.2, "percentage": 30 },
                { "value": 3.8, "percentage": 70 }
            ]
        },
        "Fisica mecanica": {
            "grades": [
                { "value": 3.5, "percentage": 50 },
                { "value": 4.0, "percentage": 50 }
            ]
        },
        "Programacion orientada a objetos": {
            "grades": [
                { "value": 2.8, "percentage": 40 },
                { "value": 3.7, "percentage": 60 }
            ]
        },
        "Logica de programacion": {
            "grades": [
                { "value": 4.8, "percentage": 100 }
            ]
        },
        "Proyecto aplicado en TIC": {
            "grades": [
                { "value": 3.0, "percentage": 100 }
            ]
        },
        "Cristologia": {
            "grades": [
                { "value": 4.5, "percentage": 50 },
                { "value": 3.5, "percentage": 50 }
            ]
        },
        "Geografia": {
            "grades": [
                { "value": 2.5, "percentage": 100 }
            ]
        }
    };

    localStorage.setItem('subjects', JSON.stringify(subjectsData));
}