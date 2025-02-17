class UnitConverter {
    round(n, unit) {
        if (typeof n !== 'number') {
            throw new Error('Value to round must be a number');
        }
        if (typeof unit !== 'string') {
            throw new Error('Unit must be a string');
        }
        if (unit in this.decimalPlaces) {
            return [Math.round(n * Math.pow(10, this.decimalPlaces[unit])) / Math.pow(10, this.decimalPlaces[unit]), unit];
        }

        return [n, unit];
    }
}

export class Imperial extends UnitConverter {
    decimalPlaces = {
        'F': 0,
        'ft': 0,
        'mph': 0,
        'inHg': 2,
    };

    convert(val, unit) {
        if (typeof val !== 'number') {
            throw new Error('Value must be a number');
        }
        
        switch (unit) {
            case 'K':
                if (val < 0) { // Kelvin cannot be negative
                    throw new Error('Invalid temperature: Kelvin cannot be negative');
                }
                return this.round(((val - 273.15) * 1.8) + 32, 'F');
            case 'm':
                return this.round(val * 3.2808, 'ft');
            case 'm/s':
                return this.round(val * 2.237, 'mph');
            case 'Pa':
                return this.round(val * 0.0002953, 'inHg');
            default:
                if (!(unit in this.decimalPlaces)) {
                    throw new Error(`Unsupported unit: ${unit}`);
                }
                return this.round(val, unit);
        }
    }
}

export class Metric extends UnitConverter{
    decimalPlaces = {
        'C': 0,
        'm': 0,
        'm/s': 0,
        'Pa': 2,
    };

    convert(val, unit) {
        if (typeof val !== 'number') {
            throw new Error('Value must be a number');
        }
        
        switch (unit) {
            case 'K':
                if (val < 0) { // Kelvin cannot be negative
                    throw new Error('Invalid temperature: Kelvin cannot be negative');
                }
                return this.round(val - 273.15, 'C');
            case 'm':
                return this.round(val, 'm');  // Keep meters as is
            case 'm/s':
                return this.round(val, 'm/s');  // Keep m/s as is
            case 'Pa':
                return this.round(val, 'Pa');  // Keep Pascal as is
            default:
                if (!(unit in this.decimalPlaces)) {
                    throw new Error(`Unsupported unit: ${unit}`);
                }
                return this.round(val, unit);
        }
    }
}