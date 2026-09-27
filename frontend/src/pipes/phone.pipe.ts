import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'phone',
  standalone: true
})
export class PhonePipe implements PipeTransform {
  transform(value: string): string {
    if (!value) return '';

     // Convert to string and remove all non-digits
    const digits = value.replace(/\D/g, '');

    // Handles US numbers with country code 1
    // Check if the number has a valid length for US formatting
    const normalized = digits.length === 11 && digits.startsWith('1') ? digits.substring(1) : digits;

    // Return original value if it doesn't match standard lengths
    if (normalized.length !== 10) {
      return value;
    }

    // Return formatted phone number
    return `(${normalized.substring(0, 3)}) ${normalized.substring(3, 6)}-${normalized.substring(6)}`;
  }
}