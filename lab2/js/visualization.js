// Visualization related functionality
class BeeVisualization {
    constructor() {
        this.dots = new Map(); // Store references to all dots
        this.trails = new Map(); // Store bee movement trails
        this.isPaused = false;
        this.showTrails = true;
        this.scoutBees = new Map(); // Track scout bees
        this.workerBees = new Map(); // Track worker bees
        this.foundPrimes = new Set(); // Track found prime numbers
        this.foundDivisors = new Set(); // Track found divisors
        this.setupControls();
    }

    setupControls() {
        // If these elements exist in the DOM
        const pauseBtn = document.getElementById('pauseVisualization');
        const trailToggle = document.getElementById('toggleTrails');

        if (pauseBtn) {
            pauseBtn.addEventListener('click', () => this.togglePause());
        }

        if (trailToggle) {
            trailToggle.addEventListener('click', () => this.toggleTrails());
        }
    }

    togglePause() {
        this.isPaused = !this.isPaused;
        const pauseBtn = document.getElementById('pauseVisualization');
        if (pauseBtn) {
            if (this.isPaused) {
                pauseBtn.innerHTML = '<i class="fas fa-play me-1"></i>Продолжить';
                pauseBtn.classList.remove('btn-outline-secondary');
                pauseBtn.classList.add('btn-outline-success');
            } else {
                pauseBtn.innerHTML = '<i class="fas fa-pause me-1"></i>Пауза';
                pauseBtn.classList.remove('btn-outline-success');
                pauseBtn.classList.add('btn-outline-secondary');
            }
        }
    }

    toggleTrails() {
        this.showTrails = !this.showTrails;

        // Show/hide all trails
        this.trails.forEach(trail => {
            trail.style.display = this.showTrails ? 'block' : 'none';
        });

        const trailToggle = document.getElementById('toggleTrails');
        if (trailToggle) {
            if (this.showTrails) {
                trailToggle.innerHTML = '<i class="fas fa-route me-1"></i>Скрыть следы';
            } else {
                trailToggle.innerHTML = '<i class="fas fa-route me-1"></i>Показать следы';
            }
        }
    }

    createDot(type, position, value, F = null, id = null) {
        // Get actual element id if not provided
        const dotId = id || `${type}-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`;

        const dot = addDot(type, position, value, F);
        if (!dot) return null;

        // Add data attribute to track dot
        dot.setAttribute('data-id', dotId);

        // Store the dot reference
        if (!this.dots.has(type)) {
            this.dots.set(type, new Map());
        }
        this.dots.get(type).set(dotId, {
            element: dot,
            position: position,
            value: value,
            F: F,
            id: dotId
        });

        // Track bees and update status panels
        if (type === 'scout-bee') {
            this.scoutBees.set(dotId, {position, value, status: 'Ищет'});
            this.updateBeeStatus('scout', dotId, 'Ищет', position);
        } else if (type === 'worker-bee') {
            this.workerBees.set(dotId, {position, value, status: 'Исследует', region: []});
            this.updateBeeStatus('worker', dotId, 'Исследует', position);
        } else if (type === 'prime') {
            this.foundPrimes.add(value);
            this.updateFoundNumbers(value, F);
        } else if (type === 'best-prime') {
            this.foundDivisors.add(value);
            this.updateFoundNumbers(value, F, true);
        }

        return dot;
    }

    updateBeeStatus(type, id, status, position, additionalInfo = null) {
        const containerId = type === 'scout' ? 'scoutBeeStatus' : 'workerBeeStatus';
        const container = document.getElementById(containerId);
        if (!container) return;

        const indicatorClass = type === 'scout' ? 'scout-indicator' : 'worker-indicator';
        let statusElem = document.getElementById(`${type}-${id}`);

        if (!statusElem) {
            statusElem = document.createElement('div');
            statusElem.id = `${type}-${id}`;
            statusElem.className = 'bee-status-item appear';
            container.appendChild(statusElem);
        }

        let statusText = `Позиция: ${position}, Статус: ${status}`;
        if (additionalInfo) {
            statusText += `, ${additionalInfo}`;
        }

        statusElem.innerHTML = `
            <span class="bee-indicator ${indicatorClass}"></span>
            <span>${statusText}</span>
        `;
    }

    updateFoundNumbers(value, F = null, isDivisor = false) {
        const container = document.getElementById('foundPrimesList');
        if (!container) return;

        // Check if this number is already displayed
        const existingBadge = document.getElementById(`prime-${value}`);
        if (existingBadge) {
            // If it's now a divisor, update the styling
            if (isDivisor) {
                existingBadge.classList.add('divisor-badge');
                // Remove tooltip attributes
                // existingBadge.setAttribute('data-bs-toggle', 'tooltip');
                // existingBadge.setAttribute('data-bs-placement', 'top');
                existingBadge.setAttribute('title', `F(${value}) = ${F.toFixed(6)}`);
            }
            return;
        }

        // Create new badge for this number
        const badge = document.createElement('span');
        badge.id = `prime-${value}`;
        badge.className = `prime-badge appear ${isDivisor ? 'divisor-badge' : ''}`;
        badge.textContent = value;

        if (F !== null) {
            // Set title attribute for basic tooltip but no Bootstrap tooltip
            // badge.setAttribute('data-bs-toggle', 'tooltip');
            // badge.setAttribute('data-bs-placement', 'top');
            badge.setAttribute('title', `F(${value}) = ${F.toFixed(6)}`);

            // Remove Bootstrap tooltip initialization
            // if (typeof bootstrap !== 'undefined') {
            //     new bootstrap.Tooltip(badge);
            // }
        }

        container.appendChild(badge);
    }

    moveBee(type, id, fromPosition, toPosition, newStatus = null, duration = 1000) {
        // Find bee element
        let beeElement;
        if (type === 'scout-bee' && this.dots.has('scout-bee')) {
            const scoutDot = this.dots.get('scout-bee').get(id);
            if (scoutDot) beeElement = scoutDot.element;
        } else if (type === 'worker-bee' && this.dots.has('worker-bee')) {
            const workerDot = this.dots.get('worker-bee').get(id);
            if (workerDot) beeElement = workerDot.element;
        }

        if (!beeElement) return Promise.resolve();

        if (this.isPaused) {
            // If paused, just update position
            const start = currentRange.start;
            const end = currentRange.end;
            const range = end - start;
            const percentPosition = ((toPosition - start) / range) * 100;
            beeElement.style.left = `${percentPosition}%`;

            // Update status
            if (type === 'scout-bee' && newStatus) {
                this.updateBeeStatus('scout', id, newStatus, toPosition);
                if (this.scoutBees.has(id)) {
                    const bee = this.scoutBees.get(id);
                    bee.position = toPosition;
                    bee.status = newStatus;
                }
            } else if (type === 'worker-bee' && newStatus) {
                this.updateBeeStatus('worker', id, newStatus, toPosition);
                if (this.workerBees.has(id)) {
                    const bee = this.workerBees.get(id);
                    bee.position = toPosition;
                    bee.status = newStatus;
                }
            }

            return Promise.resolve();
        }

        return new Promise(resolve => {
            const start = currentRange.start;
            const end = currentRange.end;
            const range = end - start;

            const fromPercent = ((fromPosition - start) / range) * 100;
            const toPercent = ((toPosition - start) / range) * 100;

            // Add trail if enabled
            if (this.showTrails) {
                const trail = document.createElement('div');
                trail.className = 'bee-trail';
                trail.style.left = `${Math.min(fromPercent, toPercent)}%`;
                trail.style.width = `${Math.abs(toPercent - fromPercent)}%`;
                trail.style.top = beeElement.offsetTop + 'px';
                elements.numberLine.appendChild(trail);

                // Store trail reference
                const trailId = `trail-${Date.now()}-${Math.random()}`;
                this.trails.set(trailId, trail);

                // Remove trail after some time
                setTimeout(() => {
                    trail.remove();
                    this.trails.delete(trailId);
                }, 5000);
            }

            // Animate move
            beeElement.style.left = `${toPercent}%`;

            // Update status
            if (type === 'scout-bee' && newStatus) {
                this.updateBeeStatus('scout', id, newStatus, toPosition);
                if (this.scoutBees.has(id)) {
                    const bee = this.scoutBees.get(id);
                    bee.position = toPosition;
                    bee.status = newStatus;
                }
            } else if (type === 'worker-bee' && newStatus) {
                this.updateBeeStatus('worker', id, newStatus, toPosition);
                if (this.workerBees.has(id)) {
                    const bee = this.workerBees.get(id);
                    bee.position = toPosition;
                    bee.status = newStatus;
                }
            }

            // Use CSS transition for smooth movement
            setTimeout(resolve, duration);
        });
    }

    updateBeeRegion(type, id, startRegion, endRegion) {
        if (type === 'worker-bee' && this.workerBees.has(id)) {
            const bee = this.workerBees.get(id);
            bee.region = [startRegion, endRegion];
            this.updateBeeStatus('worker', id, bee.status, bee.position, `Регион: [${startRegion}, ${endRegion}]`);
        }
    }

    highlightArea(start, end, color = 'rgba(255, 255, 0, 0.2)') {
        const rangeStart = currentRange.start;
        const rangeEnd = currentRange.end;
        const totalRange = rangeEnd - rangeStart;

        const startPercent = ((start - rangeStart) / totalRange) * 100;
        const width = ((end - start) / totalRange) * 100;

        const highlight = document.createElement('div');
        highlight.className = 'highlighted-area';
        highlight.style.left = `${startPercent}%`;
        highlight.style.width = `${width}%`;
        highlight.style.backgroundColor = color;
        elements.numberLine.appendChild(highlight);

        return highlight;
    }

    pulseEffect(element, duration = 1000) {
        element.classList.add('pulse-effect');
        setTimeout(() => {
            element.classList.remove('pulse-effect');
        }, duration);
    }

    clearVisualization(keepBestPrimes = false) {
        // Clear all dots except best primes if requested
        this.dots.forEach((dotsMap, type) => {
            if (keepBestPrimes && type === 'best-prime') return;

            dotsMap.forEach(dot => {
                dot.element.remove();
            });
            dotsMap.clear();
        });

        // Clear all trails
        this.trails.forEach(trail => {
            trail.remove();
        });
        this.trails.clear();

        // Clear bee status panels if not keeping best primes
        if (!keepBestPrimes) {
            // Clear scout bees
            this.scoutBees.clear();
            const scoutStatus = document.getElementById('scoutBeeStatus');
            if (scoutStatus) scoutStatus.innerHTML = '';

            // Clear worker bees
            this.workerBees.clear();
            const workerStatus = document.getElementById('workerBeeStatus');
            if (workerStatus) workerStatus.innerHTML = '';
        }
    }

    resetBeeStatuses() {
        // Clear bee status panels
        const scoutStatus = document.getElementById('scoutBeeStatus');
        if (scoutStatus) scoutStatus.innerHTML = '';

        const workerStatus = document.getElementById('workerBeeStatus');
        if (workerStatus) workerStatus.innerHTML = '';

        // Reset bee collections
        this.scoutBees.clear();
        this.workerBees.clear();
    }

    resetFoundNumbers() {
        // Clear found numbers panel
        const foundNumbersList = document.getElementById('foundPrimesList');
        if (foundNumbersList) foundNumbersList.innerHTML = '';

        // Reset number collections
        this.foundPrimes.clear();
        this.foundDivisors.clear();
    }

    updateScale(newStart, newEnd) {
        // Update all existing dots to new scale
        this.dots.forEach((dots, type) => {
            dots.forEach(dot => {
                const position = dot.position;
                const range = newEnd - newStart;
                const percentPosition = ((position - newStart) / range) * 100;

                // Hide dots outside visible range
                if (percentPosition < 0 || percentPosition > 100) {
                    dot.element.style.display = 'none';
                } else {
                    dot.element.style.display = '';
                    dot.element.style.left = `${percentPosition}%`;
                }
            });
        });
    }

    // Enhanced markers for number line
    createDetailedMarkers() {
        const container = document.createElement('div');
        container.className = 'detailed-markers';

        // Clear existing vertical lines first
        const existingLines = elements.numberLine.querySelectorAll('.vertical-line');
        existingLines.forEach(line => line.remove());

        const start = currentRange.start;
        const end = currentRange.end;
        const range = end - start;

        // Create evenly spaced markers (6 markers total)
        const markerCount = 6;
        const step = range / (markerCount - 1);

        const fixedMarkers = [];
        for (let i = 0; i < markerCount; i++) {
            const value = Math.round(start + i * step);
            const position = (i * 100) / (markerCount - 1);
            fixedMarkers.push({value, position});
        }

        // Create markers at fixed positions
        fixedMarkers.forEach(marker => {
            // Create marker with label
            const markerElement = document.createElement('div');
            markerElement.className = 'major-marker';
            markerElement.innerHTML = `<span class="marker-label">${marker.value}</span>`;
            markerElement.style.left = `${marker.position}%`;

            // Create vertical line extending from marker to visualization area
            const verticalLine = document.createElement('div');
            verticalLine.className = 'vertical-line';
            verticalLine.style.left = `${marker.position}%`;
            elements.numberLine.appendChild(verticalLine);

            container.appendChild(markerElement);
        });

        // Add additional minor vertical lines for grid effect without labels
        const minorCount = markerCount - 1; // One minor marker between each pair of major markers
        for (let i = 0; i < minorCount; i++) {
            const position = ((i + 0.5) * 100) / (markerCount - 1);

            // Add minor vertical line
            const minorVerticalLine = document.createElement('div');
            minorVerticalLine.className = 'vertical-line minor';
            minorVerticalLine.style.left = `${position}%`;
            elements.numberLine.appendChild(minorVerticalLine);

            // Create minor marker (tick only, no label)
            const minorMarker = document.createElement('div');
            minorMarker.className = 'minor-marker';
            minorMarker.style.left = `${position}%`;
            container.appendChild(minorMarker);
        }

        return container;
    }
}

// Create a global visualization instance
const beeVis = new BeeVisualization();

// Initialize Bootstrap tooltips
document.addEventListener('DOMContentLoaded', function () {
    // Remove tooltips initialization
    // if (typeof bootstrap !== 'undefined') {
    //     const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    //     tooltipTriggerList.map(function (tooltipTriggerEl) {
    //         return new bootstrap.Tooltip(tooltipTriggerEl);
    //     });
    // }

    // Create markers immediately on page load
    setTimeout(() => {
        if (elements && elements.numberLineContainer) {
            // Get values from min/max labels if they exist
            const minLabel = document.getElementById('minLabel');
            const maxLabel = document.getElementById('maxLabel');

            if (minLabel && maxLabel && minLabel.textContent && maxLabel.textContent) {
                currentRange = {
                    start: parseInt(minLabel.textContent) || 100,
                    end: parseInt(maxLabel.textContent) || 148
                };
            } else {
                // Fall back to input fields if labels aren't available or populated
                const startInput = document.getElementById('intervalStart');
                const endInput = document.getElementById('intervalEnd');

                if (startInput && endInput) {
                    currentRange = {
                        start: parseInt(startInput.value) || 100,
                        end: parseInt(endInput.value) || 148
                    };
                } else {
                    // Use fixed values as a last resort
                    currentRange = {
                        start: 100,
                        end: 148
                    };
                }

                // Update labels if they exist
                if (minLabel) minLabel.textContent = currentRange.start;
                if (maxLabel) maxLabel.textContent = currentRange.end;
            }

            // Clear existing markers
            const existingMarkers = elements.numberLineContainer.querySelector('.detailed-markers');
            if (existingMarkers) existingMarkers.remove();

            // Create and add new markers
            const markers = beeVis.createDetailedMarkers();
            elements.numberLineContainer.appendChild(markers);

            console.log("Markers initialized with range:", currentRange);
        }
    }, 200); // Slightly longer delay to ensure DOM is fully loaded
});

// Add CSS styles for the new visualization elements
document.addEventListener('DOMContentLoaded', function () {
    const style = document.createElement('style');
    style.textContent = `
        .bee-trail {
            position: absolute;
            height: 2px;
            background-color: rgba(255, 215, 0, 0.3);
            z-index: 1;
            transition: width 0.5s ease-out;
        }
        
        .highlighted-area {
            position: absolute;
            height: 100%;
            background-color: rgba(255, 255, 0, 0.2);
            z-index: 0;
            border-radius: 4px;
        }
        
        .pulse-effect {
            animation: pulse-animation 1s ease-out;
        }
        
        @keyframes pulse-animation {
            0% { transform: scale(1) translateX(-50%); }
            50% { transform: scale(1.5) translateX(-33%); }
            100% { transform: scale(1) translateX(-50%); }
        }
        
        #numberLineContainer {
            margin-bottom: 10px !important; /* Reduced from 40px to 10px since we're hiding the labels */
            height: 120px !important;
            position: relative;
            overflow: visible !important;
        }
        
        #numberLine {
            position: relative;
            background-color: #ecf0f1;
            border-radius: 4px;
            height: 60px;
            margin-top: 40px;
        }
        
        .detailed-markers {
            position: absolute;
            top: 60px;
            width: 100%;
            height: 30px;
            z-index: 10;
        }
        
        .major-marker {
            position: absolute;
            height: 10px;
            width: 1px;
            background-color: #333;
            top: 0;
            transform: translateX(-50%);
        }
        
        .minor-marker {
            position: absolute;
            height: 5px;
            width: 1px;
            background-color: #aaa;
            top: 0;
            transform: translateX(-50%);
        }
        
        .marker-label {
            position: absolute;
            top: 12px;
            left: 0;
            transform: translateX(-50%);
            font-size: 12px;
            background-color: rgba(255, 255, 255, 0.8);
            padding: 1px 3px;
            border-radius: 2px;
            white-space: nowrap;
        }
        
        .vertical-line {
            position: absolute;
            height: 100%;
            width: 1px;
            background-color: rgba(0, 0, 0, 0.2);
            z-index: 0;
            transform: translateX(-50%);
            top: 0;
        }
        
        .vertical-line.minor {
            background-color: rgba(0, 0, 0, 0.1);
        }
        
        /* Remove transition from bee movement */
        .scout-bee, .worker-bee {
            /* transition: left 0.5s ease-out; */
            transition: none !important;
        }
        
        /* Hide the min/max labels at the bottom since we already have them in the markers */
        #minLabel, #maxLabel {
            display: none !important;
        }
        
        /* Remove hover effects */
        .scout-bee:hover, .worker-bee:hover, .prime:hover, .best-prime:hover,
        .major-marker:hover, .minor-marker:hover,
        .legend-item:hover, .stat-card:hover,
        .btn:hover, .btn:focus, .btn:active,
        .prime-badge:hover, .divisor-badge:hover,
        .form-control:hover, .form-control:focus,
        .form-range:hover, .form-range:focus {
            transform: none !important;
            box-shadow: none !important;
            transition: none !important;
            cursor: default !important;
            outline: none !important;
            border-color: inherit !important;
        }
        
        /* Disable tooltips */
        [data-bs-toggle="tooltip"], [title] {
            pointer-events: none !important;
        }
        
        /* Only enable specific animations we want to keep */
        .pulse-effect {
            animation: pulse-animation 1s ease-out !important;
        }
        
        /* Disable Chart.js hover effects */
        canvas {
            pointer-events: none !important;
        }
        
        /* Disable any remaining Bootstrap tooltips */
        .tooltip, .tooltip-inner, .tooltip-arrow {
            display: none !important;
            opacity: 0 !important;
            visibility: hidden !important;
        }
    `;
    document.head.appendChild(style);
}); 