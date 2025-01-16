class UnitConverter {
    validateValue(val) {
        if (val === null || val === undefined) {
            throw new Error('Value cannot be null or undefined');
        }
        if (typeof val !== 'number') {
            throw new Error('Value must be a number');
        }
        if (isNaN(val)) {
            throw new Error('Value cannot be NaN');
        }
    }

    validateUnit(unit) {
        if (unit === null || unit === undefined) {
            throw new Error('Unit cannot be null or undefined');
        }
        if (!this.getSupportedUnits().includes(unit)) {
            throw new Error(`Unsupported source unit: ${unit}`);
        }
    }

    getSupportedUnits() {
        return Object.keys(this.decimalPlaces);
    }

    round(n, unit) {
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

    getSupportedUnits() {
        return [...super.getSupportedUnits(), 'K', 'm', 'm/s', 'Pa'];
    }

    convert(val, unit) {
        this.validateValue(val);
        this.validateUnit(unit);
        
        switch (unit) {
            case 'K':
                return this.round(((val - 273.15) * 1.8) + 32, 'F');
            case 'm':
                return this.round(val * 3.2808, 'ft');
            case 'm/s':
                return this.round(val * 2.237, 'mph');
            case 'Pa':
                return this.round(val * 0.0002953, 'inHg');
            default:
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

    getSupportedUnits() {
        return [...super.getSupportedUnits(), 'K'];
    }

    convert(val, unit) {
        this.validateValue(val);
        this.validateUnit(unit);
        
        switch (unit) {
            case 'K':
                return this.round(val - 273.15, 'C');
            default:
                return this.round(val, unit);
        }
    }
}