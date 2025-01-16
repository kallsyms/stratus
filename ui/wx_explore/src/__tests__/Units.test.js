import { Imperial, Metric } from '../Units';

describe('UnitConverter', () => {
  let imperialConverter;
  let metricConverter;

  beforeEach(() => {
    imperialConverter = new Imperial();
    metricConverter = new Metric();
  });

  describe('Input validation', () => {
    test('should throw error for non-numeric values', () => {
      expect(() => imperialConverter.convert('not a number', 'K')).toThrow('Value must be a number');
      expect(() => metricConverter.convert('invalid', 'K')).toThrow('Value must be a number');
    });

    test('should throw error for null/undefined values', () => {
      expect(() => imperialConverter.convert(null, 'K')).toThrow('Value cannot be null or undefined');
      expect(() => imperialConverter.convert(undefined, 'K')).toThrow('Value cannot be null or undefined');
      expect(() => metricConverter.convert(null, 'K')).toThrow('Value cannot be null or undefined');
      expect(() => metricConverter.convert(undefined, 'K')).toThrow('Value cannot be null or undefined');
    });

    test('should throw error for NaN values', () => {
      expect(() => imperialConverter.convert(NaN, 'K')).toThrow('Value cannot be NaN');
      expect(() => metricConverter.convert(NaN, 'K')).toThrow('Value cannot be NaN');
    });
  });

  describe('Unit validation', () => {
    test('should throw error for unsupported source units', () => {
      expect(() => imperialConverter.convert(100, 'invalid')).toThrow('Unsupported source unit: invalid');
      expect(() => metricConverter.convert(100, 'invalid')).toThrow('Unsupported source unit: invalid');
    });

    test('should throw error for null/undefined units', () => {
      expect(() => imperialConverter.convert(100, null)).toThrow('Unit cannot be null or undefined');
      expect(() => imperialConverter.convert(100, undefined)).toThrow('Unit cannot be null or undefined');
      expect(() => metricConverter.convert(100, null)).toThrow('Unit cannot be null or undefined');
      expect(() => metricConverter.convert(100, undefined)).toThrow('Unit cannot be null or undefined');
    });
  });

  describe('Valid conversions', () => {
    test('should correctly convert valid temperature values', () => {
      const [value, unit] = imperialConverter.convert(273.15, 'K');
      expect(value).toBe(32);
      expect(unit).toBe('F');
    });

    test('should correctly convert valid distance values', () => {
      const [value, unit] = imperialConverter.convert(1, 'm');
      expect(value).toBe(3);
      expect(unit).toBe('ft');
    });

    test('should correctly convert valid speed values', () => {
      const [value, unit] = imperialConverter.convert(1, 'm/s');
      expect(value).toBe(2);
      expect(unit).toBe('mph');
    });

    test('should correctly convert valid pressure values', () => {
      const [value, unit] = imperialConverter.convert(100000, 'Pa');
      expect(value).toBe(29.53);
      expect(unit).toBe('inHg');
    });
  });
});