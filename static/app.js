class NSEDataDownloader {
    constructor() {
        this.baseURL = 'http://localhost:5000/api';
        this.isDownloading = false;
        this.progressInterval = null;
        
        this.initializeElements();
        this.bindEvents();
        this.initializeApp();
    }

    initializeElements() {
        // Form elements
        this.downloadType = document.getElementById('downloadType');
        this.singleDate = document.getElementById('singleDate');
        this.startDate = document.getElementById('startDate');
        this.endDate = document.getElementById('endDate');
        this.downloadBtn = document.getElementById('downloadBtn');
        
        // Quick action buttons
        this.todayBtn = document.getElementById('todayBtn');
        this.yesterdayBtn = document.getElementById('yesterdayBtn');
        this.lastWeekBtn = document.getElementById('lastWeekBtn');
        
        // Progress elements
        this.progressRing = document.getElementById('progressRing');
        this.progressBar = document.getElementById('progressBar');
        this.progressStatus = document.getElementById('progressStatus');
        this.progressPercent = document.getElementById('progressPercent');
        this.progressDetails = document.getElementById('progressDetails');
        
        // Stats elements
        this.indiceCount = document.getElementById('indiceCount');
        this.stockCount = document.getElementById('stockCount');
        this.maCount = document.getElementById('maCount');
        this.optionCount = document.getElementById('optionCount');
        this.fiveMinCount = document.getElementById('fiveMinCount');
        
        // Status elements
        this.connectionStatus = document.getElementById('connectionStatus');
        this.statusBadge = document.getElementById('statusBadge');
        this.apiHealth = document.getElementById('apiHealth');
        this.lastDownload = document.getElementById('lastDownload');
        this.refreshBtn = document.getElementById('refreshBtn');
        
        // Form groups
        this.singleDateGroup = document.getElementById('singleDateGroup');
        this.dateRangeGroup = document.getElementById('dateRangeGroup');
    }

    bindEvents() {
        // Download type change
        this.downloadType.addEventListener('change', (e) => {
            this.toggleDateInputs(e.target.value);
        });
        
        // Download button
        this.downloadBtn.addEventListener('click', () => {
            this.startDownload();
        });
        
        // Quick action buttons
        this.todayBtn.addEventListener('click', () => {
            this.setQuickDate('today');
        });
        
        this.yesterdayBtn.addEventListener('click', () => {
            this.setQuickDate('yesterday');
        });
        
        this.lastWeekBtn.addEventListener('click', () => {
            this.setQuickDate('lastWeek');
        });
        
        // Refresh button
        this.refreshBtn.addEventListener('click', () => {
            this.refreshStatus();
        });
    }

    async initializeApp() {
        await this.checkHealth();
        await this.loadStats();
        await this.checkFolders();
        
        // Set default date to today
        this.setQuickDate('today');
        
        // Start periodic health checks
        setInterval(() => this.checkHealth(), 30000);
    }

    toggleDateInputs(type) {
        if (type === 'single') {
            this.singleDateGroup.classList.remove('hidden');
            this.dateRangeGroup.classList.add('hidden');
        } else {
            this.singleDateGroup.classList.add('hidden');
            this.dateRangeGroup.classList.remove('hidden');
        }
    }

    setQuickDate(type) {
        const today = new Date();
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        
        const formatDate = (date) => {
            return date.toISOString().split('T')[0];
        };
        
        switch (type) {
            case 'today':
                this.downloadType.value = 'single';
                this.toggleDateInputs('single');
                this.singleDate.value = formatDate(today);
                break;
            case 'yesterday':
                this.downloadType.value = 'single';
                this.toggleDateInputs('single');
                this.singleDate.value = formatDate(yesterday);
                break;
            case 'lastWeek':
                const weekAgo = new Date(today);
                weekAgo.setDate(weekAgo.getDate() - 7);
                this.downloadType.value = 'range';
                this.toggleDateInputs('range');
                this.startDate.value = formatDate(weekAgo);
                this.endDate.value = formatDate(yesterday);
                break;
        }
    }

    async makeRequest(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`API request failed for ${endpoint}:`, error);
            this.updateConnectionStatus(false);
            throw error;
        }
    }

    async checkHealth() {
        try {
            const response = await this.makeRequest('/health');
            this.updateConnectionStatus(true);
            this.apiHealth.textContent = 'Healthy';
            this.apiHealth.setAttribute('appearance', 'success');
        } catch (error) {
            this.updateConnectionStatus(false);
            this.apiHealth.textContent = 'Unhealthy';
            this.apiHealth.setAttribute('appearance', 'danger');
        }
    }

    async loadStats() {
        try {
            const stats = await this.makeRequest('/stats');
            this.indiceCount.textContent = stats.indice || 0;
            this.stockCount.textContent = stats.stock || 0;
            this.maCount.textContent = stats.ma || 0;
            this.optionCount.textContent = stats.option || 0;
            this.fiveMinCount.textContent = stats['5min_stocks'] || 0;
        } catch (error) {
            console.error('Failed to load stats:', error);
            this.setStatsError();
        }
    }

    async checkFolders() {
        try {
            const response = await this.makeRequest('/check-folders');
            const lastDate = response.lastDownloadDate;
            
            if (lastDate && lastDate !== 'No data found') {
                // Convert DDMMYYYY to readable format
                const day = lastDate.substring(0, 2);
                const month = lastDate.substring(2, 4);
                const year = lastDate.substring(4, 8);
                this.lastDownload.textContent = `${day}/${month}/${year}`;
            } else {
                this.lastDownload.textContent = 'No data found';
            }
        } catch (error) {
            console.error('Failed to check folders:', error);
            this.lastDownload.textContent = 'Error loading';
        }
    }

    updateConnectionStatus(connected) {
        if (connected) {
            this.statusBadge.textContent = 'Connected';
            this.statusBadge.setAttribute('appearance', 'success');
        } else {
            this.statusBadge.textContent = 'Disconnected';
            this.statusBadge.setAttribute('appearance', 'danger');
        }
    }

    setStatsError() {
        const elements = [this.indiceCount, this.stockCount, this.maCount, this.optionCount, this.fiveMinCount];
        elements.forEach(el => el.textContent = 'Error');
    }

    async startDownload() {
        if (this.isDownloading) return;
        
        const downloadData = this.getDownloadData();
        if (!downloadData) return;
        
        this.isDownloading = true;
        this.updateDownloadUI(true);
        
        try {
            const response = await this.makeRequest('/download-data', {
                method: 'POST',
                body: JSON.stringify(downloadData)
            });
            
            // Start progress monitoring
            this.startProgressMonitoring();
            
        } catch (error) {
            console.error('Download failed:', error);
            this.showError('Download failed: ' + error.message);
            this.resetDownloadUI();
        }
    }

    getDownloadData() {
        const type = this.downloadType.value;
        
        if (type === 'single') {
            const date = this.singleDate.value;
            if (!date) {
                this.showError('Please select a date');
                return null;
            }
            return { type: 'single', dates: date };
        } else {
            const startDate = this.startDate.value;
            const endDate = this.endDate.value;
            
            if (!startDate || !endDate) {
                this.showError('Please select both start and end dates');
                return null;
            }
            
            if (new Date(startDate) > new Date(endDate)) {
                this.showError('Start date must be before end date');
                return null;
            }
            
            return { type: 'range', dates: [startDate, endDate] };
        }
    }

    startProgressMonitoring() {
        this.progressInterval = setInterval(async () => {
            try {
                const progress = await this.makeRequest('/progress');
                this.updateProgress(progress);
                
                // Check if download is complete
                if (progress.status && progress.status.includes('completed')) {
                    this.completeDownload();
                }
            } catch (error) {
                console.error('Failed to get progress:', error);
            }
        }, 1000);
    }

    updateProgress(progress) {
        if (progress.current !== undefined && progress.total !== undefined) {
            const percentage = Math.round((progress.current / progress.total) * 100);
            
            this.progressBar.value = percentage;
            this.progressPercent.textContent = `${percentage}%`;
            
            if (progress.status) {
                this.progressStatus.textContent = progress.status;
                this.progressDetails.textContent = `Processing ${progress.current} of ${progress.total} items`;
            }
        }
    }

    completeDownload() {
        clearInterval(this.progressInterval);
        this.progressInterval = null;
        
        this.progressStatus.textContent = 'Download completed successfully!';
        this.progressPercent.textContent = '100%';
        this.progressBar.value = 100;
        
        // Refresh stats and status
        setTimeout(() => {
            this.loadStats();
            this.checkFolders();
            this.resetDownloadUI();
        }, 2000);
    }

    updateDownloadUI(downloading) {
        if (downloading) {
            this.downloadBtn.textContent = 'Downloading...';
            this.downloadBtn.disabled = true;
            this.progressRing.classList.remove('hidden');
            this.progressBar.classList.remove('hidden');
            this.progressStatus.textContent = 'Starting download...';
            this.progressPercent.textContent = '0%';
        }
    }

    resetDownloadUI() {
        this.isDownloading = false;
        this.downloadBtn.textContent = 'Start Download';
        this.downloadBtn.disabled = false;
        this.progressRing.classList.add('hidden');
        this.progressBar.classList.add('hidden');
        this.progressStatus.textContent = 'Ready to download';
        this.progressPercent.textContent = '';
        this.progressDetails.textContent = '';
        
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
    }

    async refreshStatus() {
        this.refreshBtn.disabled = true;
        this.refreshBtn.textContent = 'Refreshing...';
        
        try {
            await Promise.all([
                this.checkHealth(),
                this.loadStats(),
                this.checkFolders()
            ]);
        } catch (error) {
            console.error('Failed to refresh status:', error);
        } finally {
            this.refreshBtn.disabled = false;
            this.refreshBtn.textContent = 'Refresh Status';
        }
    }

    showError(message) {
        // Create a simple error display
        this.progressDetails.textContent = `Error: ${message}`;
        this.progressDetails.style.borderLeftColor = '#d13438';
        this.progressDetails.style.backgroundColor = '#fef2f2';
        
        setTimeout(() => {
            this.progressDetails.textContent = '';
            this.progressDetails.style.borderLeftColor = '#0078d4';
            this.progressDetails.style.backgroundColor = '#f3f2f1';
        }, 5000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new NSEDataDownloader();
});