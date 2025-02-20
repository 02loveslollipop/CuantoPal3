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