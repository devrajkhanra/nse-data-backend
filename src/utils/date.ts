import { format, isValid, parseISO } from 'date-fns';

export const formatDate = (date: Date | string, formatStr: string = 'yyyy-MM-dd'): string => {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return isValid(dateObj) ? format(dateObj, formatStr) : '';
};

export const formatDisplayDate = (dateStr: string): string => {
  if (!dateStr || dateStr === 'No data found') return dateStr;
  
  // Handle ddmmyyyy format
  if (dateStr.length === 8 && /^\d{8}$/.test(dateStr)) {
    const day = dateStr.substring(0, 2);
    const month = dateStr.substring(2, 4);
    const year = dateStr.substring(4, 8);
    const date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
    return format(date, 'MMM dd, yyyy');
  }
  
  // Handle yyyy-mm-dd format
  const date = parseISO(dateStr);
  return isValid(date) ? format(date, 'MMM dd, yyyy') : dateStr;
};

export const isValidDateString = (dateStr: string): boolean => {
  const date = parseISO(dateStr);
  return isValid(date);
};