// Core algorithm variables
let running = false;
let iterations = 0;
let primesFound = 0;
let divisorsFound = 0;
let bestPrecisionValue = Number.MAX_VALUE;
let animationSpeed = 5;
let zoomLevel = 1;
let currentRange = {start: 0, end: 0};
let fitnessChart = null; // Chart.js instance
let fitnessData = []; // Store fitness data for the chart
let startTime = null; // Store algorithm start time
let timerInterval = null; // Timer interval reference

// DOM Elements references
const elements = {
    numberInput: document.getElementById('number'),
    startBtn: document.getElementById('startBtn'),
    stopBtn: document.getElementById('stopBtn'),
    intervalStartInput: document.getElementById('intervalStart'),
    intervalEndInput: document.getElementById('intervalEnd'),
    scoutsInput: document.getElementById('scouts'),
    workersInput: document.getElementById('workers'),
    sitesInput: document.getElementById('sites'),
    precisionInput: document.getElementById('precision'),
    numberLine: document.getElementById('numberLine'),
    numberLineContainer: document.getElementById('numberLineContainer'),
    minLabel: document.getElementById('minLabel'),
    maxLabel: document.getElementById('maxLabel'),
    scoutBeeStatus: document.getElementById('scoutBeeStatus'),
    workerBeeStatus: document.getElementById('workerBeeStatus'),
    foundPrimesList: document.getElementById('foundPrimesList'),
    fitnessChart: document.getElementById('fitnessChart'),
    iterationsElement: document.getElementById('iterations'),
    primesFoundElement: document.getElementById('primesFound'),
    divisorsFoundElement: document.getElementById('divisorsFound'),
    bestPrecisionElement: document.getElementById('bestPrecision'),
    executionTimeElement: document.getElementById('executionTime'),
    speedControl: document.getElementById('speed'),
    speedValue: document.getElementById('speedValue'),
    resultPanel: document.getElementById('resultPanel'),
    factorizationResult: document.getElementById('factorizationResult'),
    statusBlock: document.getElementById('statusBlock'),
    statusIcon: document.getElementById('statusIcon'),
    statusText: document.getElementById('statusText'),
    zoomInBtn: document.getElementById('zoomIn'),
    zoomOutBtn: document.getElementById('zoomOut'),
    resetZoomBtn: document.getElementById('resetZoom'),
    pauseVisualizationBtn: document.getElementById('pauseVisualization'),
    toggleTrailsBtn: document.getElementById('toggleTrails')
};

// Initialize fitness function chart
function initFitnessChart() {
    if (!elements.fitnessChart) return;

    // Destroy existing chart if it exists
    if (fitnessChart) {
        fitnessChart.destroy();
    }

    // Reset fitness data
    fitnessData = [];

    // Create new chart with auto-scaling
    const ctx = elements.fitnessChart.getContext('2d');
    fitnessChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Значения F(x)',
                data: [],
                backgroundColor: 'rgba(46, 204, 113, 0.7)',
                borderColor: 'rgba(46, 204, 113, 1)',
                pointRadius: 5,
                pointHoverRadius: 5
            }, {
                label: 'Лучшие делители',
                data: [],
                backgroundColor: 'rgba(39, 174, 96, 1)',
                borderColor: 'rgba(20, 91, 50, 1)',
                borderWidth: 2,
                pointRadius: 7,
                pointHoverRadius: 7
            }]
        },
        options: {
            animation: false,
            responsive: true,
            maintainAspectRatio: false,
            hover: {
                mode: null,  // Disable hover interactions completely
                intersect: false
            },
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'Значение числа'
                    }
                },
                y: {
                    type: 'linear',
                    title: {
                        display: true,
                        text: 'F(x)'
                    },
                    min: 0, // Start at 0
                    // Remove fixed max to allow auto-scaling
                    ticks: {
                        precision: 6 // Increased precision
                    },
                    beginAtZero: true
                }
            },
            plugins: {
                tooltip: {
                    enabled: false,  // Disable tooltips completely
                    callbacks: {
                        label: function (context) {
                            let label = '';
                            if (context.parsed.x !== null && context.parsed.y !== null) {
                                label = `x: ${context.parsed.x}, F(x): ${context.parsed.y.toFixed(6)}`;
                            }
                            return label;
                        }
                    }
                },
                legend: {
                    position: 'top',
                    labels: {
                        boxWidth: 10,
                        font: {
                            size: 10
                        }
                    }
                }
            },
            layout: {
                padding: 0
            }
        }
    });
}

// Update fitness chart with new data
function updateFitnessChart(value, F, isDivisor = false) {
    if (!fitnessChart) return;

    // Always add the point - no filtering based on scale
    // Add data to appropriate dataset
    const datasetIndex = isDivisor ? 1 : 0;

    // Add new data point
    fitnessChart.data.datasets[datasetIndex].data.push({
        x: value,
        y: F
    });

    // Sort data by x value for better visualization
    fitnessChart.data.datasets[datasetIndex].data.sort((a, b) => a.x - b.x);

    // Update chart - axis will automatically adjust
    fitnessChart.update();
}

// Event listeners
function setupEventListeners() {
    elements.startBtn.addEventListener('click', startAlgorithm);
    elements.stopBtn.addEventListener('click', stopAlgorithm);
    elements.speedControl.addEventListener('input', updateSpeed);
    elements.zoomInBtn.addEventListener('click', () => adjustZoom(0.5));
    elements.zoomOutBtn.addEventListener('click', () => adjustZoom(2));
    elements.resetZoomBtn.addEventListener('click', resetZoom);
    elements.numberInput.addEventListener('change', calculateRecommendedRange);
}

// Initialize the application
function initApp() {
    updateSpeed();
    calculateRecommendedRange();
    setupEventListeners();
    initFitnessChart();
    updateStatus('waiting');
}

// Calculate recommended search range based on input number
function calculateRecommendedRange() {
    const N = parseInt(elements.numberInput.value);
    if (isNaN(N) || N < 4) return;

    // Square root approach for factorization
    const sqrtN = Math.floor(Math.sqrt(N));

    // Set range to be roughly around sqrt(N) with some margin
    const rangeSize = Math.max(20, Math.floor(sqrtN * 0.2));
    const start = Math.max(2, sqrtN - rangeSize);
    const end = sqrtN + rangeSize;

    elements.intervalStartInput.value = start;
    elements.intervalEndInput.value = end;

    updateRangeLabels(start, end);

    // Display message using Bootstrap toast if available
    if (typeof bootstrap !== 'undefined') {
        // Create and show toast
        const toastContainer = document.createElement('div');
        toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = 11;

        toastContainer.innerHTML = `
            <div class="toast align-items-center text-white bg-primary border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fas fa-info-circle me-2"></i>
                        Рекомендуемый интервал поиска: [${start}, ${end}] (√${N} ≈ ${sqrtN})
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;

        document.body.appendChild(toastContainer);
        const toastElement = toastContainer.querySelector('.toast');
        const toast = new bootstrap.Toast(toastElement, {delay: 3000});
        toast.show();

        // Remove toast after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastContainer.remove();
        });
    }
}

// Update the visualization speed
function updateSpeed() {
    animationSpeed = parseInt(elements.speedControl.value);
    elements.speedValue.textContent = animationSpeed + 'x';
}

// Zoom functionality
function adjustZoom(factor) {
    zoomLevel *= factor;

    const currentStart = parseInt(elements.minLabel.textContent);
    const currentEnd = parseInt(elements.maxLabel.textContent);
    const center = (currentStart + currentEnd) / 2;
    const range = currentEnd - currentStart;

    const newRange = range * factor;
    const newStart = Math.max(2, Math.floor(center - newRange / 2));
    const newEnd = Math.floor(center + newRange / 2);

    updateRangeLabels(newStart, newEnd);
    redrawNumberLine();
}

function resetZoom() {
    zoomLevel = 1;
    const start = parseInt(elements.intervalStartInput.value);
    const end = parseInt(elements.intervalEndInput.value);
    updateRangeLabels(start, end);
    redrawNumberLine();
}

function updateRangeLabels(start, end) {
    elements.minLabel.textContent = start;
    elements.maxLabel.textContent = end;
    currentRange.start = start;
    currentRange.end = end;
}

// Redraw the number line with current dots
function redrawNumberLine() {
    // Clear and regenerate markers
    elements.numberLine.innerHTML = '';

    // Create markers based on current zoom level
    if (typeof beeVis !== 'undefined') {
        const markers = beeVis.createDetailedMarkers();
        elements.numberLineContainer.appendChild(markers);

        // Update the visualization to reflect the new range
        beeVis.updateScale(currentRange.start, currentRange.end);
    } else {
        generateAxisMarkers();
    }
}

// Initialize visualization
function initVisualization() {
    const start = parseInt(elements.intervalStartInput.value);
    const end = parseInt(elements.intervalEndInput.value);

    // Clear visualization elements
    elements.numberLine.innerHTML = '';

    // Clear number markers in the container
    const existingMarkers = elements.numberLineContainer.querySelector('.detailed-markers, .number-markers');
    if (existingMarkers) existingMarkers.remove();

    // Reset statistics
    iterations = 0;
    primesFound = 0;
    divisorsFound = 0;
    bestPrecisionValue = Number.MAX_VALUE;
    updateStats();

    // Reset timer display
    elements.executionTimeElement.textContent = '00:00.00';

    // Reset range labels
    updateRangeLabels(start, end);

    // Reset fitness chart
    initFitnessChart();

    // Reset bee statuses and found numbers if using enhanced visualization
    if (typeof beeVis !== 'undefined') {
        beeVis.resetBeeStatuses();
        beeVis.resetFoundNumbers();

        // Add detailed markers
        const markers = beeVis.createDetailedMarkers();
        elements.numberLineContainer.appendChild(markers);
    } else {
        generateAxisMarkers();
    }
}

// Generate markers on the number line axis
function generateAxisMarkers() {
    const markersContainer = document.createElement('div');
    markersContainer.className = 'number-markers';

    const start = currentRange.start;
    const end = currentRange.end;
    const range = end - start;

    // Create 5 evenly spaced markers
    const step = range / 4;
    for (let i = 0; i <= 4; i++) {
        const value = Math.floor(start + step * i);
        const position = (i * 25) + '%';

        const marker = document.createElement('div');
        marker.className = 'marker';
        marker.textContent = value;
        marker.style.left = position;

        const axisLine = document.createElement('div');
        axisLine.className = 'axis-line';
        axisLine.style.left = position;

        markersContainer.appendChild(marker);
        elements.numberLine.appendChild(axisLine);
    }

    elements.numberLineContainer.appendChild(markersContainer);
}

// Add a dot to the visualization
function addDot(type, position, value, F = null) {
    const start = currentRange.start;
    const end = currentRange.end;
    const range = end - start;

    // Calculate the percentage position
    const percentPosition = ((position - start) / range) * 100;

    // Don't add dots outside the visible range
    if (percentPosition < 0 || percentPosition > 100) return null;

    const dot = document.createElement('div');
    dot.classList.add(type);
    dot.style.left = `${percentPosition}%`;

    // Add tooltip
    let tooltipText = `Значение: ${value}`;
    if (F !== null) {
        tooltipText += `, F(x) = ${F.toFixed(6)}`;
    }
    dot.title = tooltipText;

    // Remove Bootstrap tooltip 
    // if (typeof bootstrap !== 'undefined') {
    //     dot.setAttribute('data-bs-toggle', 'tooltip');
    //     dot.setAttribute('data-bs-placement', 'top');
    //     dot.setAttribute('title', tooltipText);
    // }

    elements.numberLine.appendChild(dot);
    return dot;
}

// Show alert message
function showAlert(message, type = 'primary', duration = 3000) {
    // Function disabled - no alerts will be shown

}

// Update statistics
function updateStats() {
    elements.iterationsElement.textContent = iterations;
    elements.primesFoundElement.textContent = primesFound;
    elements.bestPrecisionElement.textContent = bestPrecisionValue === Number.MAX_VALUE ? '-' : bestPrecisionValue.toFixed(6);
}

// Timer functions for tracking execution time
function startTimer() {
    // Reset and start timer
    startTime = new Date();
    updateTimer();

    // Update timer every 10ms
    timerInterval = setInterval(updateTimer, 10);
}

function updateTimer() {
    if (!startTime) return;

    const currentTime = new Date();
    const elapsedTime = new Date(currentTime - startTime);

    // Format time as MM:SS.MS
    const minutes = elapsedTime.getUTCMinutes().toString().padStart(2, '0');
    const seconds = elapsedTime.getUTCSeconds().toString().padStart(2, '0');
    const milliseconds = Math.floor(elapsedTime.getUTCMilliseconds() / 10).toString().padStart(2, '0');

    elements.executionTimeElement.textContent = `${minutes}:${seconds}.${milliseconds}`;
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

// Number theory utility functions
// Check if a number is prime
function isPrime(num) {
    if (num <= 1) return false;
    if (num <= 3) return true;
    if (num % 2 === 0 || num % 3 === 0) return false;

    for (let i = 5; i * i <= num; i += 6) {
        if (num % i === 0 || num % (i + 2) === 0) return false;
    }
    return true;
}

// Calculate F(x) - the difference between N/x and its integer part
function calculateF(num, N) {
    const division = N / num;
    const integerPart = Math.floor(division);
    return division - integerPart;
}

// Check if a number is a divisor
function isDivisor(n, y) {
    return n % y === 0;
}

// Bit length of a number
function bitLength(num) {
    return Math.floor(Math.log2(num)) + 1;
}

// Miller-Rabin primality test for large numbers
function millerRabinTest(n, k = 5) {
    if (n <= 1) return false;
    if (n <= 3) return true;
    if (n % 2 === 0) return false;

    // Express n-1 as 2^r * d
    let r = 0;
    let d = n - 1;
    while (d % 2 === 0) {
        d /= 2;
        r++;
    }

    // Test k witnesses
    for (let i = 0; i < k; i++) {
        // Choose random a in [2, n-2]
        const a = 2 + Math.floor(Math.random() * (n - 4));

        // Compute a^d mod n
        let x = modPow(a, d, n);

        if (x === 1 || x === n - 1) continue;

        let continueTest = false;
        for (let j = 0; j < r - 1; j++) {
            x = modPow(x, 2, n);
            if (x === n - 1) {
                continueTest = true;
                break;
            }
        }

        if (!continueTest) return false;
    }

    return true;
}

// Modular exponentiation
function modPow(base, exponent, modulus) {
    if (modulus === 1) return 0;
    let result = 1;
    base = base % modulus;
    while (exponent > 0) {
        if (exponent % 2 === 1) {
            result = (result * base) % modulus;
        }
        exponent = Math.floor(exponent / 2);
        base = (base * base) % modulus;
    }
    return result;
}

// Sleep function for animations
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Update status display
function updateStatus(status, message) {
    if (!elements.statusBlock) return;

    // Reset all status classes
    elements.statusBlock.classList.remove('status-waiting', 'status-running', 'status-success', 'status-failed');

    // Set appropriate icon and status
    switch (status) {
        case 'waiting':
            elements.statusBlock.classList.add('status-waiting');
            elements.statusIcon.innerHTML = '<i class="fas fa-pause-circle"></i>';
            elements.statusText.textContent = message || 'Алгоритм не запущен';
            break;
        case 'running':
            elements.statusBlock.classList.add('status-running');
            elements.statusIcon.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            elements.statusText.textContent = message || 'Алгоритм выполняется...';
            break;
        case 'success':
            elements.statusBlock.classList.add('status-success');
            elements.statusIcon.innerHTML = '<i class="fas fa-check-circle"></i>';
            elements.statusText.textContent = message || 'Делители найдены';
            break;
        case 'failed':
            elements.statusBlock.classList.add('status-failed');
            elements.statusIcon.innerHTML = '<i class="fas fa-times-circle"></i>';
            elements.statusText.textContent = message || 'Делители не найдены';
            break;
    }
}

// Main algorithm implementation
async function startAlgorithm() {
    if (running) return;

    running = true;
    elements.startBtn.style.display = 'none';
    elements.stopBtn.style.display = 'block';

    // Start the execution timer
    startTimer();

    // Update status to running and clear previous result
    updateStatus('running');
    elements.factorizationResult.textContent = '';

    // Get parameters
    const N = parseInt(elements.numberInput.value);
    const nl = parseInt(elements.intervalStartInput.value);
    const nr = parseInt(elements.intervalEndInput.value);
    const D = parseInt(elements.scoutsInput.value);
    const B = parseInt(elements.workersInput.value);
    const Z = parseInt(elements.sitesInput.value);
    const epsilon = parseFloat(elements.precisionInput.value);

    initVisualization();

    // Sets for tracking found primes and divisors
    const foundPrimes = new Set();
    const foundDivisors = new Set();

    // Map to track bee IDs
    const scoutBeeIds = new Map();
    const workerBeeIds = new Map();

    // Main algorithm loop
    while (running) {
        iterations++;
        updateStats();

        // Step 2: Choose Z points in the interval [nl, nr]
        let scoutPositions = [];
        for (let i = 0; i < Z; i++) {
            const randomPos = Math.floor(nl + Math.random() * (nr - nl));
            scoutPositions.push(randomPos);

            // Enhanced visualization using beeVis if available
            const scoutId = `scout-${iterations}-${i}`;
            scoutBeeIds.set(scoutId, {position: randomPos});

            if (typeof beeVis !== 'undefined') {
                const dot = beeVis.createDot('scout-bee', randomPos, randomPos, null, scoutId);
                if (dot) beeVis.pulseEffect(dot);
            } else {
                // Fallback to basic visualization
                await sleep(1000 / animationSpeed);
                addDot('scout-bee', randomPos, randomPos);
            }
        }

        // Array for all primes found in this iteration
        let allPrimes = [];

        // Step 3: Send worker bees to search for primes
        for (const [scoutId, scoutInfo] of scoutBeeIds.entries()) {
            const xi = scoutInfo.position;

            // Update scout status
            if (typeof beeVis !== 'undefined') {
                beeVis.updateBeeStatus('scout', scoutId, 'Определяет окрестность', xi);
            }

            // Step 3.1: Define neighborhood
            const bitCount = Math.floor(Math.log2(xi)) + 1;
            const r = Math.ceil(bitCount / 1.442695);

            const lowerBound = Math.max(nl, xi - r);
            const upperBound = Math.min(nr, xi + r);

            // Highlight explored region
            let regionHighlight;
            if (typeof beeVis !== 'undefined') {
                regionHighlight = beeVis.highlightArea(lowerBound, upperBound);
                beeVis.updateBeeStatus('scout', scoutId, 'Отправляет рабочих пчел', xi, `Окрестность: [${lowerBound}, ${upperBound}]`);
            }

            // Step 3.2 and 3.3: Check numbers in neighborhood for primality
            const localPrimes = [];

            // Distribute worker bees across the neighborhood
            const step = Math.ceil((upperBound - lowerBound) / B);
            for (let b = 0; b < B; b++) {
                const start = lowerBound + b * step;
                const end = Math.min(upperBound, start + step);

                // Create worker bee ID
                const workerId = `worker-${iterations}-${scoutId}-${b}`;
                workerBeeIds.set(workerId, {start, end});

                // Position worker bee in the middle of its segment
                const workerPosition = start + Math.floor((end - start) / 2);

                // Enhanced visualization
                if (typeof beeVis !== 'undefined') {
                    const bee = beeVis.createDot('worker-bee', workerPosition, workerPosition, null, workerId);
                    beeVis.updateBeeRegion('worker-bee', workerId, start, end);
                } else {
                    await sleep(500 / animationSpeed);
                    addDot('worker-bee', workerPosition, workerPosition);
                }

                // Check numbers for primality
                for (let y = start; y <= end; y++) {
                    // Update worker bee status
                    if (typeof beeVis !== 'undefined') {
                        beeVis.updateBeeStatus('worker', workerId, 'Проверяет', y, `Проверка ${y} на простоту`);
                    }

                    if (isPrime(y)) {
                        localPrimes.push(y);
                        if (!foundPrimes.has(y)) {
                            foundPrimes.add(y);
                            primesFound++;
                            updateStats();
                        }

                        // Calculate F(y)
                        const Fy = calculateF(y, N);

                        // Update fitness chart
                        updateFitnessChart(y, Fy);

                        // Visualize prime number
                        if (typeof beeVis !== 'undefined') {
                            const primeDot = beeVis.createDot('prime', y, y, Fy);
                            beeVis.updateBeeStatus('worker', workerId, 'Нашла простое число', y, `F(${y}) = ${Fy.toFixed(6)}`);
                        } else {
                            await sleep(200 / animationSpeed);
                            addDot('prime', y, y, Fy);
                        }

                        // Check if divisor
                        if (Fy < epsilon) {
                            foundDivisors.add(y);
                            divisorsFound++;
                            updateStats();

                            // Update fitness chart with divisor
                            updateFitnessChart(y, Fy, true);

                            // Visualize found divisor with enhanced effects
                            if (typeof beeVis !== 'undefined') {
                                const bestDot = beeVis.createDot('best-prime', y, y, Fy);
                                if (bestDot) beeVis.pulseEffect(bestDot, 2000);
                                beeVis.updateBeeStatus('worker', workerId, 'Нашла делитель!', y, `F(${y}) = ${Fy.toFixed(6)} < ${epsilon}`);
                            } else {
                                addDot('best-prime', y, y, Fy);
                            }

                            // Update best precision
                            if (Fy < bestPrecisionValue) {
                                bestPrecisionValue = Fy;
                                updateStats();
                            }
                        }

                        // Add to all primes list
                        allPrimes.push({value: y, F: Fy});
                    }

                    // Small pause for visualization
                    await sleep(50 / animationSpeed);
                }

                // Update worker bee status when done with region
                if (typeof beeVis !== 'undefined') {
                    beeVis.updateBeeStatus('worker', workerId, 'Завершила', workerPosition, `Найдено ${localPrimes.length} простых чисел`);
                }
            }

            // Remove highlight after processing region
            if (regionHighlight) {
                setTimeout(() => {
                    regionHighlight.remove();
                }, 2000 / animationSpeed);
            }

            // Update scout bee status when done with directing workers
            if (typeof beeVis !== 'undefined') {
                beeVis.updateBeeStatus('scout', scoutId, 'Завершила', xi, `Обработано ${workerBeeIds.size} рабочими пчелами`);
            }
        }

        // Step 4: Determine best solutions
        allPrimes.sort((a, b) => a.F - b.F);

        // Step 5: Choose random elements for next iteration
        // If exact divisor found, stop
        if (bestPrecisionValue === 0) {
            break;
        }

        // If no primes found, generate new random points
        if (allPrimes.length === 0) {
            // Clear existing bee IDs for the next iteration
            scoutBeeIds.clear();
            workerBeeIds.clear();
            continue;
        }

        // Send scout bees to search for new regions
        for (let d = 0; d < D; d++) {
            const randomPos = Math.floor(nl + Math.random() * (nr - nl));
            const additionalScoutId = `additional-scout-${iterations}-${d}`;

            if (typeof beeVis !== 'undefined') {
                beeVis.createDot('scout-bee', randomPos, randomPos, null, additionalScoutId);
            } else {
                await sleep(500 / animationSpeed);
                addDot('scout-bee', randomPos, randomPos);
            }
        }

        // Pause between iterations for clarity
        await sleep(2000 / animationSpeed);

        // Clear visualization for next iteration but keep best primes
        if (typeof beeVis !== 'undefined') {
            beeVis.clearVisualization(true);
        } else {
            // Basic clear
            elements.numberLine.innerHTML = '';
            generateAxisMarkers();

            // Show best divisors found
            for (const divisor of foundDivisors) {
                const F = calculateF(divisor, N);
                addDot('best-prime', divisor, divisor, F);
            }
        }

        // Clear existing bee IDs for the next iteration
        scoutBeeIds.clear();
        workerBeeIds.clear();

        // Stop condition
        if (iterations >= 10) {
            break;
        }
    }

    // Display factorization results
    if (foundDivisors.size > 0) {
        let resultText = `${N} = `;
        const divisorsArray = Array.from(foundDivisors);
        divisorsArray.sort((a, b) => a - b);

        // Check if any of the found divisors is an exact divisor
        let exactDivisorFound = false;

        for (const divisor of divisorsArray) {
            const F = calculateF(divisor, N);
            const quotient = Math.floor(N / divisor);
            const remainder = N % divisor;

            if (isDivisor(N, divisor)) {
                exactDivisorFound = true;
                const otherFactor = N / divisor;

                resultText += `${divisor} × ${otherFactor}`;
                break;
            }
        }

        // If no exact divisor was found, use the best approximation
        if (!exactDivisorFound && divisorsArray.length > 0) {
            const bestDivisor = divisorsArray.reduce((a, b) =>
                calculateF(a, N) < calculateF(b, N) ? a : b);

            const approxFactor = Math.floor(N / bestDivisor);
            resultText += `≈ ${bestDivisor} × ${approxFactor} (приближенное разложение)`;
        }

        elements.factorizationResult.textContent = resultText;

        // Update status to success
        updateStatus('success');
    } else {
        // Update status to failed
        updateStatus('failed', 'Делители не найдены');
    }

    running = false;
    elements.startBtn.style.display = 'block';
    elements.stopBtn.style.display = 'none';

    // Stop the execution timer
    stopTimer();
}

// Stop the algorithm
function stopAlgorithm() {
    running = false;
    elements.startBtn.style.display = 'block';
    elements.stopBtn.style.display = 'none';

    // Stop the execution timer
    stopTimer();

    // Update status to waiting
    updateStatus('waiting', 'Алгоритм остановлен');
}

// Initialize app on load
document.addEventListener('DOMContentLoaded', initApp); 