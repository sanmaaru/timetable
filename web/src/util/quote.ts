import quoteData from '../resources/quotes.json';
import {getRandomInt} from "./common";

export interface Quote {
    quote: string;
    source: string;
}

export const getRandomQuote = (): Quote => {
    const num_quotes = quoteData.quotes.length;
    return getQuote(getRandomInt(num_quotes));
}

export const getQuote = (index: number): Quote => {
    const quotes = quoteData.quotes;
    return quotes[index];
}